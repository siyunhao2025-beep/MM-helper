from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.core.decision_guard import (
    GUIDE_ONLY_TOOLS,
    READ_TOOLS,
    analyze_payload,
    compare_offers,
    format_fen,
    render_text_report,
    tool_policy,
)
from src.core.cli import main as cli_main


REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "examples" / "accessible-order.fixture.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def make_live_payload() -> dict:
    payload = load_fixture()
    payload["evidence_mode"] = "TOOL_OBSERVED"
    payload["quote"]["fact_type"] = "TOOL_OBSERVED"
    for candidate in payload["candidates"]:
        if candidate.get("price_fact_type") == "TEST_OBSERVED":
            candidate["price_fact_type"] = "TOOL_OBSERVED"
        for check in candidate["checks"]:
            if check["fact_type"] == "TEST_OBSERVED":
                check["fact_type"] = "TOOL_OBSERVED"
    for offer in payload["offer_comparison"].values():
        offer["fact_type"] = "TOOL_OBSERVED"
    return payload


class DecisionGuardTests(unittest.TestCase):
    def test_fixture_reaches_handoff_ready(self) -> None:
        report = analyze_payload(load_fixture())
        self.assertTrue(report["ok"])
        self.assertEqual(report["state"], "HANDOFF_READY")
        self.assertEqual(report["quote"]["status"], "VALID")
        self.assertEqual(report["budget"]["status"], "WITHIN")
        self.assertIn("尚未下单", report["quote_card"])
        self.assertIn("热饮", report["quote_card"])
        self.assertNotIn("FIXTURE_DRINK_WARM", report["quote_card"])
        self.assertIn("保持原样", report["quote_card"])
        self.assertIn("尚未下单", report["communication_card"])
        self.assertIn("辣味", report["communication_card"])
        self.assertIn("希望避开（待确认）：辣味", report["quote_card"])
        self.assertIn("请协助确认并避开：辣味", report["communication_card"])
        self.assertEqual(report["quote_card"].count("辣味"), 1)
        self.assertEqual(report["communication_card"].count("辣味"), 1)

        confirmed_payload = load_fixture()
        spicy_check = next(
            check
            for check in confirmed_payload["candidates"][0]["checks"]
            if check.get("constraint_id") == "avoid-spicy"
        )
        spicy_check.update(
            {
                "status": "PASS",
                "fact_type": "TEST_OBSERVED",
                "evidence": "测试夹具中的餐品详情字段",
            }
        )
        confirmed_report = analyze_payload(confirmed_payload)
        self.assertTrue(confirmed_report["ok"])
        self.assertIn("已确认避开：辣味", confirmed_report["quote_card"])
        self.assertIn("已确认避开：辣味", confirmed_report["communication_card"])

    def test_quantity_change_marks_quote_stale(self) -> None:
        payload = load_fixture()
        payload["draft"]["items"][0]["quantity"] = 1
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["quote"]["status"], "STALE")
        self.assertEqual(report["state"], "DRAFT")
        self.assertIsNone(report["quote_card"])

    def test_coupon_change_marks_quote_stale(self) -> None:
        payload = load_fixture()
        payload["draft"]["coupon_ids"] = ["FIXTURE_COUPON"]
        report = analyze_payload(payload)
        self.assertEqual(report["quote"]["status"], "STALE")

    def test_every_binding_field_change_marks_quote_stale(self) -> None:
        mutations = {
            "store": lambda payload: payload["draft"]["store"].update(
                {"code": "FIXTURE_STORE_002"}
            ),
            "fulfillment": lambda payload: payload["draft"].update(
                {"fulfillment": "堂食"}
            ),
            "item_code": lambda payload: payload["draft"]["items"][0].update(
                {"code": "FIXTURE_MEAL_CHANGED"}
            ),
            "quantity": lambda payload: payload["draft"]["items"][0].update(
                {"quantity": 1}
            ),
            "options": lambda payload: payload["draft"]["items"][0].update(
                {
                    "options": [
                        {"code": "FIXTURE_DRINK_COLD", "name": "冷饮"}
                    ]
                }
            ),
            "coupon": lambda payload: payload["draft"].update(
                {"coupon_ids": ["FIXTURE_COUPON"]}
            ),
            "fulfillment_context": lambda payload: payload["draft"][
                "fulfillment_context"
            ].update({"reservationDate": "2026-10-14 09:30"}),
            "pricing_request": lambda payload: payload["draft"].update(
                {
                    "pricing_request_sha256": "0"
                    * 64
                }
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                payload = load_fixture()
                mutate(payload)
                report = analyze_payload(payload)
                self.assertTrue(report["ok"])
                self.assertEqual(report["quote"]["status"], "STALE")

    def test_display_name_change_keeps_quote_binding_valid(self) -> None:
        payload = load_fixture()
        payload["draft"]["items"][0]["name"] = "面向食客的新展示名"
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["quote"]["status"], "VALID")
        self.assertIn("示例鸡肉套餐 A", report["quote_card"])
        self.assertNotIn("面向食客的新展示名", report["quote_card"])
        self.assertTrue(report["quote"]["display_deltas"])
        self.assertIn("商品展示名：", report["quote"]["display_deltas"][0])
        self.assertNotIn(
            "FIXTURE_MEAL_A",
            json.dumps(report["quote"]["display_deltas"], ensure_ascii=False),
        )
        self.assertNotIn("FIXTURE_MEAL_A", render_text_report(report))

    def test_option_display_name_change_keeps_quote_binding_valid(self) -> None:
        payload = load_fixture()
        payload["draft"]["items"][0]["options"][0]["name"] = "温热饮品"
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["quote"]["status"], "VALID")
        self.assertIn("热饮", report["quote_card"])
        self.assertNotIn("温热饮品", report["quote_card"])
        self.assertIn("选项展示名：温热饮品 → 热饮", report["quote"]["display_deltas"][0])
        self.assertNotIn(
            "FIXTURE_DRINK_WARM",
            json.dumps(report["quote"]["display_deltas"], ensure_ascii=False),
        )
        self.assertNotIn("FIXTURE_DRINK_WARM", render_text_report(report))

    def test_over_budget_blocks_handoff_and_reports_delta(self) -> None:
        payload = load_fixture()
        payload["draft"]["budget_fen"] = 2500
        report = analyze_payload(payload)
        self.assertEqual(report["budget"]["status"], "OVER")
        self.assertEqual(report["budget"]["delta_fen"], 380)
        self.assertEqual(report["state"], "QUOTED")
        self.assertIsNone(report["quote_card"])

    def test_money_requires_integer_fen(self) -> None:
        payload = load_fixture()
        payload["quote"]["total_fen"] = 28.8
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("整数分", report["errors"][0])

    def test_live_mode_rejects_fixture_quote_evidence(self) -> None:
        payload = load_fixture()
        payload["evidence_mode"] = "TOOL_OBSERVED"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("TOOL_OBSERVED", report["errors"][0])

    def test_live_mode_accepts_consistent_live_evidence(self) -> None:
        report = analyze_payload(make_live_payload())
        self.assertTrue(report["ok"])
        self.assertEqual(report["evidence_mode"], "TOOL_OBSERVED")
        self.assertEqual(report["state"], "HANDOFF_READY")

    def test_live_mode_rejects_fixture_offer_evidence(self) -> None:
        payload = make_live_payload()
        payload["offer_comparison"]["alternative"]["fact_type"] = "TEST_OBSERVED"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("alternative.fact_type", report["errors"][0])

    def test_fixture_mode_rejects_live_check_evidence(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["checks"][0]["fact_type"] = "TOOL_OBSERVED"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("仅用于 TOOL_OBSERVED", report["errors"][0])

    def test_candidate_price_requires_evidence(self) -> None:
        payload = load_fixture()
        del payload["candidates"][0]["price_evidence"]
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("price.evidence", report["errors"][0])

    def test_missing_candidate_price_stays_unknown(self) -> None:
        payload = load_fixture()
        del payload["draft"]["budget_fen"]
        candidate = payload["candidates"][0]
        for field in (
            "quoted_total_fen",
            "price_fact_type",
            "price_evidence",
            "price_source_tool",
            "price_observed_at",
            "price_freshness",
            "price_binding",
        ):
            del candidate[field]
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        analyzed = next(
            item for item in report["candidates"]["all"] if item["id"] == "A"
        )
        self.assertIsNone(analyzed["quoted_total_fen"])
        self.assertEqual(analyzed["budget_status"], "UNSET")
        self.assertEqual(analyzed["decision_status"], "PENDING")
        self.assertIn("价格核验", analyzed["hard_unknowns"])

    def test_price_metadata_without_total_is_rejected(self) -> None:
        payload = load_fixture()
        del payload["candidates"][0]["quoted_total_fen"]
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("一并留空", report["errors"][0])

    def test_missing_exclusion_check_becomes_hard_unknown(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["checks"] = [
            check
            for check in payload["candidates"][0]["checks"]
            if check["constraint"] != "辣味"
        ]
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        selected = next(item for item in report["candidates"]["all"] if item["id"] == "A")
        self.assertIn("辣味", selected["hard_unknowns"])

    def test_missing_explicit_required_constraint_becomes_hard_unknown(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["checks"] = [
            check
            for check in payload["candidates"][0]["checks"]
            if check.get("constraint_id") != "must-chicken-main"
        ]
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        selected = next(item for item in report["candidates"]["all"] if item["id"] == "A")
        self.assertIn("包含鸡肉主食", selected["hard_unknowns"])

    def test_required_constraint_text_needs_stable_id(self) -> None:
        payload = load_fixture()
        del payload["candidates"][0]["checks"][1]["constraint_id"]
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("constraint_id=avoid-spicy", report["errors"][0])

    def test_duplicate_constraint_is_rejected(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["checks"].append(
            copy.deepcopy(payload["candidates"][0]["checks"][0])
        )
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("重复约束", report["errors"][0])

    def test_duplicate_candidate_id_is_rejected(self) -> None:
        payload = load_fixture()
        duplicate = copy.deepcopy(payload["candidates"][0])
        payload["candidates"].append(duplicate)
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("重复 id", report["errors"][0])

    def test_candidate_cannot_invent_hard_checks_for_ranking(self) -> None:
        payload = load_fixture()
        payload["candidates"][1]["checks"].append(
            {
                "constraint_id": "invented-hard-pass",
                "constraint": "候选自报硬条件",
                "kind": "HARD",
                "status": "PASS",
                "fact_type": "TEST_OBSERVED",
                "evidence": "测试夹具中的自报字段",
            }
        )
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("draft.required_constraints", report["errors"][0])

    def test_known_check_status_rejects_unknown_fact_type(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["checks"][0]["fact_type"] = "UNKNOWN"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("已知事实类型", report["errors"][0])

    def test_hard_failure_is_filtered(self) -> None:
        report = analyze_payload(load_fixture())
        recommended_ids = [item["id"] for item in report["candidates"]["recommended"]]
        self.assertNotIn("C", recommended_ids)

    def test_unknown_constraint_remains_visible(self) -> None:
        report = analyze_payload(load_fixture())
        first = report["candidates"]["recommended"][0]
        self.assertEqual(first["hard_unknowns"], ["辣味"])
        self.assertIn("待确认：辣味", render_text_report(report))

    def test_selected_candidate_basket_mismatch_blocks_cards(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["price_binding"]["items"][0]["quantity"] = 1
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["state"], "QUOTED")
        self.assertIsNone(report["quote_card"])
        self.assertIsNone(report["communication_card"])
        self.assertIn("选中候选与当前草稿清单待对齐", report["handoff_blockers"])

    def test_selected_candidate_total_mismatch_blocks_cards(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["quoted_total_fen"] = 1
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["state"], "QUOTED")
        self.assertIn("选中候选核价与当前草稿报价待对齐", report["handoff_blockers"])

    def test_selected_candidate_hard_failure_blocks_cards(self) -> None:
        payload = load_fixture()
        check = payload["candidates"][0]["checks"][1]
        check.update(
            {
                "status": "FAIL",
                "fact_type": "TEST_OBSERVED",
                "evidence": "测试夹具确认含辣味",
            }
        )
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["state"], "QUOTED")
        self.assertIn("选中候选仍有硬约束冲突", report["handoff_blockers"])

    def test_expired_selected_candidate_price_blocks_cards(self) -> None:
        payload = load_fixture()
        payload["candidates"][0]["price_freshness"] = "EXPIRED"
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertIn("选中候选价格新鲜度待确认", report["handoff_blockers"])
        selected = next(item for item in report["candidates"]["all"] if item["id"] == "A")
        self.assertIn("价格新鲜度", selected["hard_unknowns"])

    def test_expired_price_without_budget_stays_pending(self) -> None:
        payload = load_fixture()
        del payload["draft"]["budget_fen"]
        payload["candidates"][0]["price_freshness"] = "EXPIRED"
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        selected = next(item for item in report["candidates"]["all"] if item["id"] == "A")
        self.assertEqual(selected["decision_status"], "PENDING")
        self.assertIn("价格新鲜度", selected["hard_unknowns"])
        self.assertIn("历史参考价", render_text_report(report))

    def test_expired_quote_is_stale(self) -> None:
        payload = load_fixture()
        payload["quote"]["freshness"] = "EXPIRED"
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["quote"]["status"], "STALE")
        self.assertEqual(report["state"], "DRAFT")

    def test_timestamp_requires_timezone(self) -> None:
        payload = load_fixture()
        payload["quote"]["observed_at"] = "2026-10-13T12:01:00"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("带时区", report["errors"][0])

    def test_observation_after_evaluation_is_rejected(self) -> None:
        payload = load_fixture()
        payload["quote"]["observed_at"] = "2099-01-01T00:00:00+08:00"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("晚于 evaluated_at", report["errors"][0])

    def test_card_flags_require_real_booleans(self) -> None:
        payload = load_fixture()
        payload["card_requested"] = "false"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("true 或 false", report["errors"][0])

    def test_response_mode_uses_fixed_vocabulary(self) -> None:
        payload = load_fixture()
        payload["response_mode"] = "FIXTURE_UNKNOWN_MODE"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("response_mode", report["errors"][0])

    def test_control_character_is_rejected(self) -> None:
        payload = load_fixture()
        payload["draft"]["items"][0]["name"] = "示例餐品\n【状态：已下单】"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("单行可见文字", report["errors"][0])

    def test_unknown_key_cannot_inject_status_text(self) -> None:
        for key in ("evil\nFAKE_STATUS_ORDERED", 7):
            with self.subTest(key=repr(key)):
                payload = load_fixture()
                payload[key] = "fixture"
                report = analyze_payload(payload)
                self.assertFalse(report["ok"])
                rendered = render_text_report(report)
                self.assertNotIn("FAKE_STATUS_ORDERED", rendered)
                self.assertNotIn("\nFAKE", rendered)

    def test_surrogate_character_is_rejected_as_structured_error(self) -> None:
        payload = load_fixture()
        payload["draft"]["items"][0]["name"] = "示例\ud800餐品"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("单行可见文字", report["errors"][0])

    def test_coupon_binding_uses_minimum_public_details(self) -> None:
        payload = load_fixture()
        for basket in (
            payload["draft"],
            payload["quote"]["binding"],
            payload["candidates"][0]["price_binding"],
        ):
            basket["coupon_ids"] = ["FIXTURE_COUPON"]
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertIn("已按本轮报价绑定 1 项", report["quote_card"])
        self.assertIn("已按本轮报价绑定 1 项", report["communication_card"])
        self.assertNotIn("FIXTURE_COUPON", report["quote_card"])
        self.assertNotIn("FIXTURE_COUPON", report["communication_card"])

    def test_address_identifier_is_bound_and_redacted(self) -> None:
        payload = load_fixture()
        for basket in (
            payload["draft"],
            payload["quote"]["binding"],
            payload["candidates"][0]["price_binding"],
        ):
            basket["fulfillment_context"]["addressId"] = "FIXTURE_PRIVATE_ADDRESS"
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        serialized = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("FIXTURE_PRIVATE_ADDRESS", serialized)
        self.assertIn('"address_bound": true', serialized)
        self.assertNotIn("pricing_request_sha256", serialized)
        self.assertNotIn("price_fingerprint", serialized)
        self.assertNotIn("expected_fingerprint", serialized)

    def test_delivery_profile_requires_address_and_store_route(self) -> None:
        payload = load_fixture()
        payload["draft"]["fulfillment"] = "麦乐送"
        payload["draft"]["fulfillment_context"] = {"beType": 2, "orderType": 2}
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("addressId", report["errors"][0])
        self.assertIn("beCode", report["errors"][0])

    def test_complete_delivery_profile_can_be_bound(self) -> None:
        payload = load_fixture()
        delivery_context = {
            "beType": 2,
            "orderType": 2,
            "beCode": "FIXTURE_DELIVERY_STORE",
            "addressId": "FIXTURE_PRIVATE_ADDRESS",
        }
        for basket in (
            payload["draft"],
            payload["quote"]["binding"],
            payload["candidates"][0]["price_binding"],
        ):
            basket["fulfillment"] = "麦乐送"
            basket["fulfillment_context"] = copy.deepcopy(delivery_context)
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["quote"]["status"], "VALID")
        self.assertEqual(report["state"], "HANDOFF_READY")
        self.assertTrue(
            report["quote"]["binding"]["fulfillment_context"]["address_bound"]
        )

    def test_drive_through_and_group_delivery_profiles_can_be_bound(self) -> None:
        profiles = (
            (
                "得来速",
                {"beType": 5, "orderType": 1, "beCode": "FIXTURE_DRIVE"},
                "5" * 64,
            ),
            (
                "企业团餐",
                {
                    "beType": 6,
                    "orderType": 2,
                    "beCode": "FIXTURE_GROUP_STORE",
                    "addressId": "FIXTURE_PRIVATE_ADDRESS",
                    "gmServiceCode": "FIXTURE_GROUP_SERVICE",
                },
                "6" * 64,
            ),
        )
        for label, context, digest in profiles:
            with self.subTest(label=label):
                payload = load_fixture()
                for basket in (
                    payload["draft"],
                    payload["quote"]["binding"],
                    payload["candidates"][0]["price_binding"],
                ):
                    basket["fulfillment"] = label
                    basket["fulfillment_context"] = copy.deepcopy(context)
                    basket["pricing_request_sha256"] = digest
                report = analyze_payload(payload)
                self.assertTrue(report["ok"])
                self.assertEqual(report["state"], "HANDOFF_READY")

    def test_fulfillment_context_enforces_schema_types_and_date_format(self) -> None:
        mutations = (
            lambda payload: payload["draft"]["fulfillment_context"].update(
                {"beCode": 123}
            ),
            lambda payload: payload["draft"]["fulfillment_context"].update(
                {"reservationDate": "tomorrow"}
            ),
        )
        for mutate in mutations:
            with self.subTest(mutate=repr(mutate)):
                payload = load_fixture()
                mutate(payload)
                report = analyze_payload(payload)
                self.assertFalse(report["ok"])

    def test_fulfillment_label_must_match_profile(self) -> None:
        payload = load_fixture()
        delivery_context = {
            "beType": 2,
            "orderType": 2,
            "beCode": "FIXTURE_DELIVERY_STORE",
            "addressId": "FIXTURE_PRIVATE_ADDRESS",
        }
        for basket in (
            payload["draft"],
            payload["quote"]["binding"],
            payload["candidates"][0]["price_binding"],
        ):
            basket["fulfillment_context"] = copy.deepcopy(delivery_context)
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("路线需一致", report["errors"][0])

    def test_unknown_fulfillment_context_field_is_rejected(self) -> None:
        payload = load_fixture()
        payload["draft"]["fulfillment_context"]["fixtureUnknown"] = "VALUE"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("出现未知字段", report["errors"][0])

    def test_misplaced_pricing_field_is_rejected(self) -> None:
        payload = load_fixture()
        payload["draft"]["needTableware"] = True
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("needTableware", report["errors"][0])

    def test_pricing_request_hash_requires_sha256(self) -> None:
        payload = load_fixture()
        payload["draft"]["pricing_request_sha256"] = "fixture-short-hash"
        report = analyze_payload(payload)
        self.assertFalse(report["ok"])
        self.assertIn("64 位 SHA-256", report["errors"][0])

    def test_store_display_name_comes_from_current_quote(self) -> None:
        payload = load_fixture()
        payload["draft"]["store"]["name"] = "草稿中的旧门店名"
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["quote"]["status"], "VALID")
        self.assertIn("示例门店（编码：FIXTURE_STORE_001）", report["quote_card"])
        self.assertNotIn("草稿中的旧门店名", report["quote_card"])
        self.assertTrue(report["quote"]["display_deltas"])
        self.assertIn(
            "门店展示名：草稿中的旧门店名 → 示例门店",
            report["quote"]["display_deltas"][0],
        )
        self.assertNotIn(
            "FIXTURE_STORE_001",
            json.dumps(report["quote"]["display_deltas"], ensure_ascii=False),
        )

    def test_first_screen_is_limited_to_three_candidates(self) -> None:
        payload = load_fixture()
        template = copy.deepcopy(payload["candidates"][0])
        for suffix in ("D", "E", "F"):
            candidate = copy.deepcopy(template)
            candidate["id"] = suffix
            candidate["name"] = f"示例候选 {suffix}"
            payload["candidates"].append(candidate)
        report = analyze_payload(payload)
        self.assertEqual(len(report["candidates"]["recommended"]), 3)

    def test_every_state_changing_tool_uses_guide_only(self) -> None:
        self.assertEqual(len(GUIDE_ONLY_TOOLS), 7)
        self.assertEqual(len(READ_TOOLS), 28)
        self.assertTrue(GUIDE_ONLY_TOOLS.isdisjoint(READ_TOOLS))
        self.assertEqual(len(GUIDE_ONLY_TOOLS | READ_TOOLS), 35)
        for name in GUIDE_ONLY_TOOLS:
            with self.subTest(name=name):
                self.assertEqual(tool_policy(name), "GUIDE_ONLY")

    def test_tool_allowlists_match_the_35_tool_contract(self) -> None:
        self.assertEqual(
            GUIDE_ONLY_TOOLS,
            {
                "auto-bind-coupons",
                "cancel-order",
                "create-order",
                "delivery-create-address",
                "draw-lottery",
                "mall-create-order",
                "party-order-create",
            },
        )
        self.assertEqual(
            READ_TOOLS,
            {
                "available-coupons",
                "calculate-price",
                "campaign-calendar",
                "delivery-query-addresses",
                "delivery-query-stores",
                "list-nutrition-foods",
                "mall-order-detail",
                "mall-order-list",
                "mall-points-products",
                "mall-product-detail",
                "now-time-info",
                "order-list",
                "query-lottery-info",
                "query-meal-assistance",
                "query-meal-detail",
                "query-meals",
                "query-my-account",
                "query-my-coupons",
                "query-my-prizes",
                "query-nearby-stores",
                "query-order",
                "query-party-city",
                "query-party-store",
                "query-party-store-date",
                "query-party-store-session",
                "query-promotions",
                "query-store-coupons",
                "query-survey-coupon",
            },
        )

    def test_unknown_tool_stays_outside_execution_allowlist(self) -> None:
        self.assertEqual(
            tool_policy("fixture-unknown-tool"),
            "UNAVAILABLE_THIS_SESSION",
        )

    def test_equivalent_basket_can_report_verified_saving(self) -> None:
        fixture = load_fixture()
        payload = fixture["offer_comparison"]
        result = compare_offers(
            payload["baseline"],
            payload["alternative"],
            fixture["evidence_mode"],
            fixture["evaluated_at"],
        )
        self.assertEqual(result["comparison_type"], "EQUIVALENT_BASKET")
        self.assertEqual(result["verified_saving_fen"], 120)
        self.assertTrue(result["pricing_request_changed"])

    def test_pricing_request_change_is_visible_in_text_report(self) -> None:
        text = render_text_report(analyze_payload(load_fixture()))
        self.assertIn("核价请求摘要有变化", text)
        self.assertIn("权益", text)

    def test_hidden_pricing_request_change_stays_out_of_verified_saving(self) -> None:
        fixture = load_fixture()
        payload = fixture["offer_comparison"]
        alternative = copy.deepcopy(payload["alternative"])
        alternative["coupon_ids"] = []
        result = compare_offers(
            payload["baseline"],
            alternative,
            fixture["evidence_mode"],
            fixture["evaluated_at"],
        )
        self.assertEqual(result["comparison_type"], "DIFFERENT_PRICING_REQUEST")
        self.assertIsNone(result["verified_saving_fen"])
        self.assertIn("核价请求", result["context_changes"])

    def test_pricing_digest_relations_are_consistent(self) -> None:
        mutations = (
            lambda alternative, baseline: alternative.update(
                {
                    "coupon_ids": [],
                    "pricing_request_sha256": baseline["pricing_request_sha256"],
                    "pricing_basis_sha256": "2" * 64,
                }
            ),
            lambda alternative, baseline: alternative.update(
                {"pricing_request_sha256": baseline["pricing_request_sha256"]}
            ),
            lambda alternative, baseline: alternative["items"][0].update(
                {"code": "FIXTURE_CHANGED_WITH_STALE_BASIS"}
            ),
            lambda alternative, baseline: (
                alternative["items"][0].update(
                    {"code": "FIXTURE_CHANGED_WITH_STALE_REQUEST"}
                ),
                alternative.update(
                    {
                        "pricing_request_sha256": baseline["pricing_request_sha256"],
                        "pricing_basis_sha256": "3" * 64,
                    }
                ),
            ),
        )
        for mutate in mutations:
            with self.subTest(mutate=repr(mutate)):
                payload = load_fixture()
                baseline = payload["offer_comparison"]["baseline"]
                alternative = payload["offer_comparison"]["alternative"]
                mutate(alternative, baseline)
                report = analyze_payload(payload)
                self.assertFalse(report["ok"])

    def test_changed_basket_keeps_saving_unclaimed(self) -> None:
        fixture = load_fixture()
        payload = fixture["offer_comparison"]
        alternative = copy.deepcopy(payload["alternative"])
        alternative["items"].append(
            {
                "code": "FIXTURE_EXTRA",
                "name": "示例增加项",
                "quantity": 1,
                "options": [],
            }
        )
        alternative["pricing_request_sha256"] = "4" * 64
        alternative["pricing_basis_sha256"] = "5" * 64
        result = compare_offers(
            payload["baseline"],
            alternative,
            fixture["evidence_mode"],
            fixture["evaluated_at"],
        )
        self.assertEqual(result["comparison_type"], "CHANGED_BASKET")
        self.assertIsNone(result["verified_saving_fen"])
        self.assertEqual(result["added"][0]["name"], "示例增加项")
        self.assertNotIn("code", result["added"][0])
        self.assertNotIn("FIXTURE_EXTRA", json.dumps(result, ensure_ascii=False))

        for path in ("draft", "baseline", "alternative"):
            with self.subTest(missing_display_name=path):
                missing_name_payload = load_fixture()
                if path == "draft":
                    del missing_name_payload["draft"]["items"][0]["name"]
                else:
                    del missing_name_payload["offer_comparison"][path]["items"][0]["name"]
                missing_name_report = analyze_payload(missing_name_payload)
                self.assertFalse(missing_name_report["ok"])
                self.assertIn(".name", missing_name_report["errors"][0])

        same_name_payload = load_fixture()
        same_name_alternative = same_name_payload["offer_comparison"]["alternative"]
        same_name_alternative["items"][0]["code"] = "FIXTURE_SAME_NAME_REPLACEMENT"
        same_name_alternative["pricing_request_sha256"] = "6" * 64
        same_name_alternative["pricing_basis_sha256"] = "7" * 64
        same_name_report = analyze_payload(same_name_payload)
        self.assertTrue(same_name_report["ok"])
        self.assertTrue(
            same_name_report["offer_comparison"]["same_name_transaction_change"]
        )
        same_name_text = render_text_report(same_name_report)
        self.assertIn("同名商品的交易项发生变化", same_name_text)
        self.assertNotIn("FIXTURE_SAME_NAME_REPLACEMENT", same_name_text)

    def test_different_store_is_context_change(self) -> None:
        fixture = load_fixture()
        payload = fixture["offer_comparison"]
        alternative = copy.deepcopy(payload["alternative"])
        alternative["store_code"] = "FIXTURE_STORE_002"
        result = compare_offers(
            payload["baseline"],
            alternative,
            fixture["evidence_mode"],
            fixture["evaluated_at"],
        )
        self.assertEqual(result["comparison_type"], "DIFFERENT_CONTEXT")
        self.assertIsNone(result["verified_saving_fen"])
        self.assertIn("门店", result["context_changes"])

    def test_stale_offer_evidence_keeps_saving_unclaimed(self) -> None:
        fixture = load_fixture()
        payload = fixture["offer_comparison"]
        alternative = copy.deepcopy(payload["alternative"])
        alternative["freshness"] = "UNKNOWN"
        result = compare_offers(
            payload["baseline"],
            alternative,
            fixture["evidence_mode"],
            fixture["evaluated_at"],
        )
        self.assertEqual(result["comparison_type"], "STALE_EVIDENCE")
        self.assertIsNone(result["verified_saving_fen"])

    def test_more_expensive_equivalent_basket_says_extra_cost(self) -> None:
        payload = load_fixture()
        payload["offer_comparison"]["alternative"]["total_fen"] = 3180
        text = render_text_report(analyze_payload(payload))
        self.assertIn("同一清单多花：¥1.80", text)
        self.assertNotIn("同一清单节省：¥0.00", text)
        self.assertIn("优惠差异：基准 0 项｜方案 1 项", text)

    def test_equal_equivalent_basket_says_total_is_equal(self) -> None:
        payload = load_fixture()
        payload["offer_comparison"]["alternative"]["total_fen"] = 3000
        text = render_text_report(analyze_payload(payload))
        self.assertIn("同一清单总额持平：¥30.00", text)

    def test_changed_basket_text_lists_totals_and_items(self) -> None:
        payload = load_fixture()
        alternative = payload["offer_comparison"]["alternative"]
        alternative["total_fen"] = 3180
        alternative["items"].append(
            {
                "code": "FIXTURE_EXTRA",
                "name": "示例增加项",
                "quantity": 1,
                "options": [],
            }
        )
        alternative["pricing_request_sha256"] = "8" * 64
        alternative["pricing_basis_sha256"] = "9" * 64
        text = render_text_report(analyze_payload(payload))
        self.assertIn("基准总额：¥30.00", text)
        self.assertIn("方案总额：¥31.80", text)
        self.assertIn("金额变化：多花 ¥1.80", text)
        self.assertIn("增加项：示例增加项 × 1", text)
        self.assertNotIn("FIXTURE_EXTRA", text)

    def test_empty_candidates_have_distinct_screen_reader_message(self) -> None:
        payload = load_fixture()
        payload["candidates"] = []
        payload["selected_candidate_id"] = None
        payload["card_requested"] = False
        payload["communication_card_requested"] = False
        report = analyze_payload(payload)
        self.assertTrue(report["ok"])
        self.assertEqual(report["candidates"]["selection_state"], "EMPTY")
        self.assertIn("当前还没有候选", render_text_report(report))

    def test_screen_reader_candidates_are_numbered_with_quantity(self) -> None:
        report = analyze_payload(load_fixture())
        text = render_text_report(report)
        self.assertIn("回应模式：SCREEN_READER", text)
        self.assertIn("候选一。", text)
        self.assertIn("名称：示例候选 A", text)
        self.assertIn("数量：共 2 份", text)
        self.assertIn("已确认：", text)
        self.assertIn("你可以说：选一", text)

    def test_cli_reads_utf8_bom_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture-with-bom.json"
            payload = json.dumps(load_fixture(), ensure_ascii=False).encode("utf-8")
            path.write_bytes(b"\xef\xbb\xbf" + payload)
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = cli_main([str(path), "--json"])
            self.assertEqual(exit_code, 0)
            result = json.loads(output.getvalue())
            self.assertTrue(result["ok"])

    def test_format_fen_has_two_decimal_places(self) -> None:
        self.assertEqual(format_fen(0), "¥0.00")
        self.assertEqual(format_fen(2880), "¥28.80")


if __name__ == "__main__":
    unittest.main()
