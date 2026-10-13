"""Deterministic guards for a ManManDian meal draft.

This module deliberately performs no network call and no state-changing action. It
accepts user-provided constraints plus already-observed tool data, then checks the
basket/quote binding, ranks evidence-backed candidates, and renders an accessible
handoff card. All money values are integer fen.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence


GUIDE_ONLY_TOOLS = frozenset(
    {
        "auto-bind-coupons",
        "cancel-order",
        "create-order",
        "delivery-create-address",
        "draw-lottery",
        "mall-create-order",
        "party-order-create",
    }
)

READ_TOOLS = frozenset(
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
    }
)

ALLOWED_EVIDENCE_MODES = frozenset({"TEST_FIXTURE", "TOOL_OBSERVED"})
ALLOWED_FACT_TYPES = frozenset(
    {
        "USER_PROVIDED",
        "TOOL_OBSERVED",
        "DOC_CONFIRMED",
        "TEST_OBSERVED",
        "INFERENCE",
        "UNKNOWN",
    }
)
OBSERVED_FACT_TYPES = frozenset(
    {"TOOL_OBSERVED", "DOC_CONFIRMED", "TEST_OBSERVED"}
)
ALLOWED_CHECK_KINDS = frozenset({"HARD", "SOFT"})
ALLOWED_CHECK_STATUSES = frozenset({"PASS", "FAIL", "UNKNOWN"})
ALLOWED_FRESHNESS = frozenset({"CURRENT", "EXPIRED", "UNKNOWN"})
ALLOWED_RESPONSE_MODES = frozenset({"STANDARD", "SCREEN_READER"})
ALLOWED_FULFILLMENT_CONTEXT = frozenset(
    {
        "addressId",
        "beCode",
        "beType",
        "gmServiceCode",
        "orderType",
        "reservationDate",
        "takeWayCode",
    }
)
FULFILLMENT_LABELS = {
    (1, 1): frozenset({"到店", "到店自取", "堂食", "外带"}),
    (5, 1): frozenset({"得来速"}),
    (2, 2): frozenset({"外送", "麦乐送"}),
    (6, 2): frozenset({"企业团餐", "团餐"}),
}
RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


class GuardInputError(ValueError):
    """Raised when input cannot be assessed without inventing missing facts."""


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GuardInputError(f"{label} 需要对象结构")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GuardInputError(f"{label} 需要数组结构")
    return value


def _reject_unknown_keys(
    value: Mapping[str, Any], allowed: Iterable[str], label: str
) -> None:
    keys: list[str] = []
    for raw_key in value:
        if not isinstance(raw_key, str):
            raise GuardInputError(f"{label} 的字段名需要单行可见文字")
        key = _require_text(raw_key, f"{label} 的字段名")
        if key != raw_key:
            raise GuardInputError(f"{label} 的字段名需要保持原样")
        keys.append(key)
    unknown = sorted(set(keys) - set(allowed))
    if unknown:
        raise GuardInputError(f"{label} 出现未知字段：{'；'.join(unknown)}")


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GuardInputError(f"{label} 需要非空文字")
    normalized = value.strip()
    if any(
        unicodedata.category(character) in {"Cc", "Cf", "Cs", "Zl", "Zp"}
        for character in normalized
    ):
        raise GuardInputError(f"{label} 需要单行可见文字")
    return normalized


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise GuardInputError(f"{label} 需要 true 或 false")
    return value


def _require_timestamp(value: Any, label: str) -> str:
    normalized = _require_text(value, label)
    if RFC3339_PATTERN.fullmatch(normalized) is None:
        raise GuardInputError(f"{label} 需要带时区的 RFC3339 时间")
    candidate = normalized[:-1] + "+00:00" if normalized.endswith("Z") else normalized
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise GuardInputError(f"{label} 需要带时区的 RFC3339 时间") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise GuardInputError(f"{label} 需要带时区的 RFC3339 时间")
    return normalized


def _timestamp_value(value: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(candidate)


def _require_observed_by(observed_at: str, evaluated_at: str, label: str) -> None:
    if _timestamp_value(observed_at) > _timestamp_value(evaluated_at):
        raise GuardInputError(f"{label} 晚于 evaluated_at")


def _require_freshness(value: Any, label: str) -> str:
    freshness = _require_text(value, label)
    if freshness not in ALLOWED_FRESHNESS:
        raise GuardInputError(f"{label} 需要 CURRENT、EXPIRED 或 UNKNOWN")
    return freshness


def _require_fen(value: Any, label: str) -> int:
    if not _is_int(value) or value < 0:
        raise GuardInputError(f"{label} 需要大于或等于 0 的整数分")
    return value


def _require_sha256(value: Any, label: str) -> str:
    digest = _require_text(value, label).lower()
    if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise GuardInputError(f"{label} 需要 64 位 SHA-256")
    return digest


def _text_list(value: Any, label: str) -> list[str]:
    values = _require_list(value, label)
    return [_require_text(item, f"{label} 项") for item in values]


def _normalize_options(value: Any, label: str) -> list[dict[str, str]]:
    options = _require_list(value, label)
    normalized: list[dict[str, str]] = []
    codes: set[str] = set()
    for index, raw in enumerate(options, start=1):
        option = _require_mapping(raw, f"{label}[{index}]")
        _reject_unknown_keys(option, {"code", "name"}, f"{label}[{index}]")
        code = _require_text(option.get("code"), f"{label}[{index}].code")
        name = _require_text(option.get("name"), f"{label}[{index}].name")
        if code in codes:
            raise GuardInputError(f"{label} 出现重复选项编码：{code}")
        codes.add(code)
        normalized.append({"code": code, "name": name})
    return sorted(normalized, key=lambda option: option["code"])


def _normalize_items(value: Any, label: str) -> list[dict[str, Any]]:
    items = _require_list(value, label)
    if not items:
        raise GuardInputError(f"{label} 至少包含一项")

    normalized: list[dict[str, Any]] = []
    signatures: set[tuple[str, tuple[str, ...]]] = set()
    for index, raw in enumerate(items, start=1):
        item = _require_mapping(raw, f"{label}[{index}]")
        _reject_unknown_keys(
            item,
            {"code", "name", "quantity", "options"},
            f"{label}[{index}]",
        )
        code = _require_text(item.get("code"), f"{label}[{index}].code")
        name = _require_text(item.get("name"), f"{label}[{index}].name")
        quantity = item.get("quantity")
        if not _is_int(quantity) or quantity < 1:
            raise GuardInputError(f"{label}[{index}].quantity 需要正整数")
        options = _normalize_options(item.get("options", []), f"{label}[{index}].options")
        signature = (code, tuple(option["code"] for option in options))
        if signature in signatures:
            raise GuardInputError(f"{label} 出现重复商品与选项组合：{code}")
        signatures.add(signature)
        normalized.append(
            {
                "code": code,
                "name": name,
                "quantity": quantity,
                "options": options,
            }
        )

    return sorted(
        normalized,
        key=lambda item: (
            item["code"],
            tuple(option["code"] for option in item["options"]),
        ),
    )


def _normalize_fulfillment_context(value: Any, label: str) -> dict[str, Any]:
    context = _require_mapping({} if value is None else value, label)
    _reject_unknown_keys(context, ALLOWED_FULFILLMENT_CONTEXT, label)
    normalized: dict[str, Any] = {}
    for key in sorted(context):
        raw = context[key]
        if key in {"beType", "orderType"}:
            if not _is_int(raw) or raw < 0:
                raise GuardInputError(f"{label}.{key} 需要非负整数")
            item: Any = raw
        else:
            item = _require_text(raw, f"{label}.{key}")
        if key == "reservationDate":
            if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", item) is None:
                raise GuardInputError(
                    f"{label}.reservationDate 需要 yyyy-MM-dd HH:mm"
                )
            try:
                datetime.strptime(item, "%Y-%m-%d %H:%M")
            except ValueError as error:
                raise GuardInputError(
                    f"{label}.reservationDate 需要有效日期时间"
                ) from error
        normalized[key] = item

    be_type = normalized.get("beType")
    order_type = normalized.get("orderType")
    if not _is_int(be_type) or not _is_int(order_type):
        raise GuardInputError(f"{label} 需要整数 beType 与 orderType")
    profile = (be_type, order_type)
    allowed_profiles = {(1, 1), (5, 1), (2, 2), (6, 2)}
    if profile not in allowed_profiles:
        raise GuardInputError(f"{label} 的 beType / orderType 组合仍待适配")
    required_by_profile = {
        (1, 1): set(),
        (5, 1): {"beCode"},
        (2, 2): {"addressId", "beCode"},
        (6, 2): {"addressId", "beCode", "gmServiceCode"},
    }
    missing = sorted(required_by_profile[profile] - set(normalized))
    if missing:
        raise GuardInputError(f"{label} 缺少当前履约路线字段：{'；'.join(missing)}")
    return normalized


def _public_basket(basket: Mapping[str, Any]) -> dict[str, Any]:
    context = dict(basket["fulfillment_context"])
    address_bound = "addressId" in context
    context.pop("addressId", None)
    if address_bound:
        context["address_bound"] = True
    return {
        "store_code": basket["store_code"],
        "store_name": basket["store_name"],
        "fulfillment": basket["fulfillment"],
        "items": basket["items"],
        "coupon_count": len(basket["coupon_ids"]),
        "fulfillment_context": context,
        "pricing_request_bound": True,
    }


def _normalize_fulfillment(
    value: Any, context: Mapping[str, Any], label: str
) -> str:
    fulfillment = _require_text(value, label)
    profile = (context["beType"], context["orderType"])
    if fulfillment not in FULFILLMENT_LABELS[profile]:
        expected = "、".join(sorted(FULFILLMENT_LABELS[profile]))
        raise GuardInputError(
            f"{label} 与 beType / orderType 路线需一致，可用：{expected}"
        )
    return fulfillment


def _basket_from_draft(draft: Mapping[str, Any]) -> dict[str, Any]:
    _reject_unknown_keys(
        draft,
        {
            "budget_fen",
            "coupon_ids",
            "exclusions",
            "fulfillment",
            "fulfillment_context",
            "items",
            "people",
            "pending_confirmations",
            "pricing_request_sha256",
            "required_constraints",
            "store",
            "wants",
        },
        "draft",
    )
    store = _require_mapping(draft.get("store"), "draft.store")
    _reject_unknown_keys(store, {"code", "name", "observed_at"}, "draft.store")
    context = _normalize_fulfillment_context(
        draft.get("fulfillment_context"), "draft.fulfillment_context"
    )
    return {
        "store_code": _require_text(store.get("code"), "draft.store.code"),
        "store_name": _require_text(store.get("name"), "draft.store.name"),
        "fulfillment": _normalize_fulfillment(
            draft.get("fulfillment"), context, "draft.fulfillment"
        ),
        "items": _normalize_items(draft.get("items"), "draft.items"),
        "coupon_ids": sorted(_text_list(draft.get("coupon_ids", []), "draft.coupon_ids")),
        "fulfillment_context": context,
        "pricing_request_sha256": _require_sha256(
            draft.get("pricing_request_sha256"), "draft.pricing_request_sha256"
        ),
    }


def _required_constraints(draft: Mapping[str, Any]) -> list[dict[str, str]]:
    raw_constraints = _require_list(
        draft.get("required_constraints", []), "draft.required_constraints"
    )
    constraints: list[dict[str, str]] = []
    ids: set[str] = set()
    texts: set[str] = set()
    for index, raw in enumerate(raw_constraints, start=1):
        item = _require_mapping(raw, f"draft.required_constraints[{index}]")
        _reject_unknown_keys(
            item,
            {"id", "user_text"},
            f"draft.required_constraints[{index}]",
        )
        constraint_id = _require_text(
            item.get("id"), f"draft.required_constraints[{index}].id"
        )
        user_text = _require_text(
            item.get("user_text"),
            f"draft.required_constraints[{index}].user_text",
        )
        if constraint_id in ids:
            raise GuardInputError(f"draft.required_constraints 出现重复 id：{constraint_id}")
        if user_text in texts:
            raise GuardInputError(
                f"draft.required_constraints 出现重复用户要求：{user_text}"
            )
        ids.add(constraint_id)
        texts.add(user_text)
        constraints.append({"id": constraint_id, "user_text": user_text})

    exclusions = _text_list(draft.get("exclusions", []), "draft.exclusions")
    for exclusion in exclusions:
        if exclusion in texts:
            continue
        digest = hashlib.sha256(exclusion.encode("utf-8")).hexdigest()[:12]
        constraint_id = f"exclusion-{digest}"
        ids.add(constraint_id)
        texts.add(exclusion)
        constraints.append({"id": constraint_id, "user_text": exclusion})
    return constraints


def _basket_from_binding(
    binding: Mapping[str, Any],
    label: str = "quote.binding",
    allowed_extra: Iterable[str] = (),
) -> dict[str, Any]:
    _reject_unknown_keys(
        binding,
        {
            "store_code",
            "store_name",
            "fulfillment",
            "items",
            "coupon_ids",
            "fulfillment_context",
            "pricing_request_sha256",
            *allowed_extra,
        },
        label,
    )
    context = _normalize_fulfillment_context(
        binding.get("fulfillment_context"), f"{label}.fulfillment_context"
    )
    return {
        "store_code": _require_text(binding.get("store_code"), f"{label}.store_code"),
        "store_name": _require_text(binding.get("store_name"), f"{label}.store_name"),
        "fulfillment": _normalize_fulfillment(
            binding.get("fulfillment"), context, f"{label}.fulfillment"
        ),
        "items": _normalize_items(binding.get("items"), f"{label}.items"),
        "coupon_ids": sorted(
            _text_list(binding.get("coupon_ids", []), f"{label}.coupon_ids")
        ),
        "fulfillment_context": context,
        "pricing_request_sha256": _require_sha256(
            binding.get("pricing_request_sha256"), f"{label}.pricing_request_sha256"
        ),
    }


def _fingerprint(value: Mapping[str, Any]) -> str:
    canonical = {
        "store_code": value["store_code"],
        "fulfillment": value["fulfillment"],
        "items": [
            {
                "code": item["code"],
                "quantity": item["quantity"],
                "options": [option["code"] for option in item["options"]],
            }
            for item in value["items"]
        ],
        "coupon_ids": value["coupon_ids"],
        "fulfillment_context": value["fulfillment_context"],
        "pricing_request_sha256": value["pricing_request_sha256"],
    }
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _display_deltas(
    draft_basket: Mapping[str, Any], quote_basket: Mapping[str, Any]
) -> list[str]:
    draft_items = {
        (
            item["code"],
            tuple(option["code"] for option in item["options"]),
        ): item
        for item in draft_basket["items"]
    }
    deltas: list[str] = []
    if draft_basket["store_name"] != quote_basket["store_name"]:
        deltas.append(
            "门店展示名："
            + draft_basket["store_name"]
            + " → "
            + quote_basket["store_name"]
        )
    for quote_item in quote_basket["items"]:
        signature = (
            quote_item["code"],
            tuple(option["code"] for option in quote_item["options"]),
        )
        draft_item = draft_items.get(signature)
        if draft_item is None:
            continue
        if draft_item["name"] != quote_item["name"]:
            deltas.append(
                f"商品展示名：{draft_item['name']} → {quote_item['name']}"
            )
        draft_names = {
            option["code"]: option["name"] for option in draft_item["options"]
        }
        for option in quote_item["options"]:
            old_name = draft_names.get(option["code"])
            if old_name is not None and old_name != option["name"]:
                deltas.append(
                    f"选项展示名：{old_name} → {option['name']}"
                )
    return deltas


def _require_dynamic_fact(
    fact_type: Any, evidence: Any, evidence_mode: str, label: str
) -> tuple[str, str]:
    normalized_type = _require_text(fact_type, f"{label}.fact_type")
    normalized_evidence = _require_text(evidence, f"{label}.evidence")
    required_type = (
        "TEST_OBSERVED" if evidence_mode == "TEST_FIXTURE" else "TOOL_OBSERVED"
    )
    if normalized_type != required_type:
        raise GuardInputError(
            f"{label}.fact_type 在 {evidence_mode} 模式需要 {required_type}"
        )
    return normalized_type, normalized_evidence


def _require_mode_compatible_fact(
    fact_type: str, evidence_mode: str, label: str
) -> None:
    if evidence_mode == "TOOL_OBSERVED" and fact_type == "TEST_OBSERVED":
        raise GuardInputError(f"{label} 的测试观察证据仅用于 TEST_FIXTURE")
    if evidence_mode == "TEST_FIXTURE" and fact_type == "TOOL_OBSERVED":
        raise GuardInputError(f"{label} 的工具观察证据仅用于 TOOL_OBSERVED")


def _item_counter(items: Sequence[Mapping[str, Any]]) -> Counter[tuple[str, tuple[str, ...]]]:
    counter: Counter[tuple[str, tuple[str, ...]]] = Counter()
    for item in items:
        counter[
            (item["code"], tuple(option["code"] for option in item["options"]))
        ] += item["quantity"]
    return counter


def _option_names_by_signature(
    items: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, tuple[str, ...]], list[str]]:
    result: dict[tuple[str, tuple[str, ...]], list[str]] = {}
    for item in items:
        signature = (
            item["code"],
            tuple(option["code"] for option in item["options"]),
        )
        result[signature] = [option["name"] for option in item["options"]]
    return result


def _item_names_by_signature(
    items: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, tuple[str, ...]], str]:
    result: dict[tuple[str, tuple[str, ...]], str] = {}
    for item in items:
        signature = (
            item["code"],
            tuple(option["code"] for option in item["options"]),
        )
        result[signature] = item["name"]
    return result


def format_fen(value: int) -> str:
    """Format an integer-fen amount as a two-decimal RMB string."""

    amount = _require_fen(value, "金额")
    return f"¥{amount // 100}.{amount % 100:02d}"


def tool_policy(short_name: str) -> str:
    """Return the local execution policy for a short MCP tool name."""

    name = _require_text(short_name, "工具名")
    if name in GUIDE_ONLY_TOOLS:
        return "GUIDE_ONLY"
    if name in READ_TOOLS:
        return "CURRENT_SCHEMA_REQUIRED"
    return "UNAVAILABLE_THIS_SESSION"


def _priced_offer(
    raw: Mapping[str, Any], label: str, evidence_mode: str, evaluated_at: str
) -> dict[str, Any]:
    total_fen = _require_fen(raw.get("total_fen"), f"{label}.total_fen")
    source_tool = _require_text(raw.get("source_tool"), f"{label}.source_tool")
    if source_tool != "calculate-price":
        raise GuardInputError(f"{label}.source_tool 需要 calculate-price")
    observed_at = _require_timestamp(raw.get("observed_at"), f"{label}.observed_at")
    _require_observed_by(observed_at, evaluated_at, f"{label}.observed_at")
    freshness = _require_freshness(raw.get("freshness"), f"{label}.freshness")
    fact_type, evidence = _require_dynamic_fact(
        raw.get("fact_type"), raw.get("evidence"), evidence_mode, label
    )
    basket = _basket_from_binding(
        raw,
        label,
        {
            "evidence",
            "fact_type",
            "freshness",
            "observed_at",
            "pricing_basis_sha256",
            "source_tool",
            "total_fen",
        },
    )
    pricing_basis_sha256 = _require_sha256(
        raw.get("pricing_basis_sha256"), f"{label}.pricing_basis_sha256"
    )
    return {
        "total_fen": total_fen,
        "source_tool": source_tool,
        "observed_at": observed_at,
        "freshness": freshness,
        "fact_type": fact_type,
        "evidence": evidence,
        "basket": basket,
        "fingerprint": _fingerprint(basket),
        "pricing_basis_sha256": pricing_basis_sha256,
    }


def compare_offers(
    baseline: Mapping[str, Any],
    alternative: Mapping[str, Any],
    evidence_mode: str,
    evaluated_at: str,
) -> dict[str, Any]:
    """Compare two evidenced quotes while keeping context changes explicit."""

    if evidence_mode not in ALLOWED_EVIDENCE_MODES:
        raise GuardInputError("evidence_mode 需要 TEST_FIXTURE 或 TOOL_OBSERVED")
    evaluated_at = _require_timestamp(evaluated_at, "evaluated_at")
    base = _priced_offer(
        _require_mapping(baseline, "baseline"),
        "baseline",
        evidence_mode,
        evaluated_at,
    )
    alt = _priced_offer(
        _require_mapping(alternative, "alternative"),
        "alternative",
        evidence_mode,
        evaluated_at,
    )
    base_counter = _item_counter(base["basket"]["items"])
    alt_counter = _item_counter(alt["basket"]["items"])
    base_item_names = _item_names_by_signature(base["basket"]["items"])
    alt_item_names = _item_names_by_signature(alt["basket"]["items"])
    base_option_names = _option_names_by_signature(base["basket"]["items"])
    alt_option_names = _option_names_by_signature(alt["basket"]["items"])
    same_demand = base_counter == alt_counter
    same_context = (
        base["basket"]["store_code"] == alt["basket"]["store_code"]
        and base["basket"]["fulfillment"] == alt["basket"]["fulfillment"]
        and base["basket"]["fulfillment_context"]
        == alt["basket"]["fulfillment_context"]
    )
    both_current = base["freshness"] == alt["freshness"] == "CURRENT"
    coupon_ids_changed = (
        base["basket"]["coupon_ids"] != alt["basket"]["coupon_ids"]
    )
    pricing_request_changed = (
        base["basket"]["pricing_request_sha256"]
        != alt["basket"]["pricing_request_sha256"]
    )
    pricing_basis_match = (
        base["pricing_basis_sha256"] == alt["pricing_basis_sha256"]
    )
    pricing_material_changed = (
        not same_demand
        or base["basket"]["fulfillment_context"]
        != alt["basket"]["fulfillment_context"]
    )
    if coupon_ids_changed and not pricing_request_changed:
        raise GuardInputError(
            "优惠标识变化时，精确核价请求摘要需要同步变化"
        )
    if not pricing_request_changed and not pricing_basis_match:
        raise GuardInputError(
            "精确核价请求摘要一致时，比较基准摘要也需要一致"
        )
    if pricing_material_changed and not pricing_request_changed:
        raise GuardInputError(
            "商品或履约参数变化时，精确核价请求摘要需要同步变化"
        )
    if pricing_material_changed and pricing_basis_match:
        raise GuardInputError(
            "商品或履约参数变化时，比较基准摘要需要同步变化"
        )
    pricing_request_comparable = (
        not pricing_request_changed
        or coupon_ids_changed
        and pricing_basis_match
    )
    spend_change = alt["total_fen"] - base["total_fen"]

    added: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for signature in sorted(set(base_counter) | set(alt_counter)):
        difference = alt_counter[signature] - base_counter[signature]
        option_names = (
            alt_option_names.get(signature, [])
            if difference > 0
            else base_option_names.get(signature, [])
        )
        item_name = (
            alt_item_names[signature]
            if difference > 0
            else base_item_names[signature]
        )
        record = {
            "name": item_name,
            "options": option_names,
            "quantity": abs(difference),
        }
        if difference > 0:
            added.append(record)
        elif difference < 0:
            removed.append(record)

    added_display_signatures = {
        (item["name"], tuple(item["options"])) for item in added
    }
    removed_display_signatures = {
        (item["name"], tuple(item["options"])) for item in removed
    }
    same_name_transaction_change = bool(
        added_display_signatures & removed_display_signatures
    )

    context_changes: list[str] = []
    if base["basket"]["store_code"] != alt["basket"]["store_code"]:
        context_changes.append("门店")
    if base["basket"]["fulfillment"] != alt["basket"]["fulfillment"]:
        context_changes.append("取餐方式")
    if (
        base["basket"]["fulfillment_context"]
        != alt["basket"]["fulfillment_context"]
    ):
        context_changes.append("履约参数")
    if not both_current:
        context_changes.append("报价新鲜度")
    if same_demand and not pricing_request_comparable:
        context_changes.append("核价请求")

    if not same_context:
        comparison_type = "DIFFERENT_CONTEXT"
    elif not both_current:
        comparison_type = "STALE_EVIDENCE"
    elif same_demand and not pricing_request_comparable:
        comparison_type = "DIFFERENT_PRICING_REQUEST"
    elif same_demand:
        comparison_type = "EQUIVALENT_BASKET"
    else:
        comparison_type = "CHANGED_BASKET"

    comparable = comparison_type == "EQUIVALENT_BASKET"
    return {
        "comparison_type": comparison_type,
        "baseline_total_fen": base["total_fen"],
        "alternative_total_fen": alt["total_fen"],
        "spend_change_fen": spend_change,
        "verified_saving_fen": max(0, -spend_change) if comparable else None,
        "verified_extra_cost_fen": max(0, spend_change) if comparable else None,
        "baseline_observed_at": base["observed_at"],
        "alternative_observed_at": alt["observed_at"],
        "baseline_coupon_count": len(base["basket"]["coupon_ids"]),
        "alternative_coupon_count": len(alt["basket"]["coupon_ids"]),
        "coupon_selection_changed": coupon_ids_changed,
        "pricing_request_changed": pricing_request_changed,
        "pricing_basis_match": pricing_basis_match,
        "context_changes": context_changes,
        "added": added,
        "removed": removed,
        "same_name_transaction_change": same_name_transaction_change,
    }


def _analyze_quote(
    draft: Mapping[str, Any], quote: Any, evidence_mode: str, evaluated_at: str
) -> dict[str, Any]:
    expected_basket = _basket_from_draft(draft)
    expected_fingerprint = _fingerprint(expected_basket)
    if quote is None:
        return {
            "status": "MISSING",
            "binding_status": "MISSING",
            "freshness": "UNKNOWN",
            "binding": None,
            "display_deltas": [],
            "total_fen": None,
        }

    quote_map = _require_mapping(quote, "quote")
    _reject_unknown_keys(
        quote_map,
        {
            "binding",
            "evidence",
            "fact_type",
            "freshness",
            "observed_at",
            "source_tool",
            "total_fen",
        },
        "quote",
    )
    source_tool = _require_text(quote_map.get("source_tool"), "quote.source_tool")
    total_fen = _require_fen(quote_map.get("total_fen"), "quote.total_fen")
    observed_at = _require_timestamp(quote_map.get("observed_at"), "quote.observed_at")
    _require_observed_by(observed_at, evaluated_at, "quote.observed_at")
    freshness = _require_freshness(quote_map.get("freshness"), "quote.freshness")
    fact_type, evidence = _require_dynamic_fact(
        quote_map.get("fact_type"),
        quote_map.get("evidence"),
        evidence_mode,
        "quote",
    )
    binding = _basket_from_binding(
        _require_mapping(quote_map.get("binding"), "quote.binding"),
        "quote.binding",
    )
    observed_fingerprint = _fingerprint(binding)
    binding_status = (
        "MATCH" if observed_fingerprint == expected_fingerprint else "MISMATCH"
    )
    status = (
        "VALID"
        if source_tool == "calculate-price"
        and binding_status == "MATCH"
        and freshness == "CURRENT"
        else "STALE"
    )
    return {
        "status": status,
        "binding_status": binding_status,
        "source_tool": source_tool,
        "fact_type": fact_type,
        "evidence": evidence,
        "observed_at": observed_at,
        "freshness": freshness,
        "binding": _public_basket(binding),
        "display_deltas": _display_deltas(expected_basket, binding),
        "total_fen": total_fen,
    }


def _analyze_budget(draft: Mapping[str, Any], quote: Mapping[str, Any]) -> dict[str, Any]:
    raw_budget = draft.get("budget_fen")
    if raw_budget is None:
        return {"status": "UNSET", "budget_fen": None, "delta_fen": None}
    budget = _require_fen(raw_budget, "draft.budget_fen")
    if quote["status"] != "VALID":
        return {"status": "PENDING", "budget_fen": budget, "delta_fen": None}

    total = quote["total_fen"]
    if total <= budget:
        return {"status": "WITHIN", "budget_fen": budget, "delta_fen": budget - total}
    return {"status": "OVER", "budget_fen": budget, "delta_fen": total - budget}


def _analyze_check(
    raw: Any, candidate_label: str, index: int, evidence_mode: str
) -> dict[str, Any]:
    check = _require_mapping(raw, f"{candidate_label}.checks[{index}]")
    _reject_unknown_keys(
        check,
        {"constraint", "constraint_id", "evidence", "fact_type", "kind", "status"},
        f"{candidate_label}.checks[{index}]",
    )
    constraint = _require_text(
        check.get("constraint"), f"{candidate_label}.checks[{index}].constraint"
    )
    raw_constraint_id = check.get("constraint_id")
    constraint_id = (
        None
        if raw_constraint_id is None
        else _require_text(
            raw_constraint_id,
            f"{candidate_label}.checks[{index}].constraint_id",
        )
    )
    kind = _require_text(check.get("kind"), f"{candidate_label}.checks[{index}].kind")
    status = _require_text(
        check.get("status"), f"{candidate_label}.checks[{index}].status"
    )
    fact_type = _require_text(
        check.get("fact_type"), f"{candidate_label}.checks[{index}].fact_type"
    )
    evidence = check.get("evidence", "")
    if not isinstance(evidence, str):
        raise GuardInputError(f"{candidate_label}.checks[{index}].evidence 需要文字")
    evidence = evidence.strip()

    if kind not in ALLOWED_CHECK_KINDS:
        raise GuardInputError(f"{candidate_label} 的检查类型需要 HARD 或 SOFT")
    if status not in ALLOWED_CHECK_STATUSES:
        raise GuardInputError(f"{candidate_label} 的检查状态需要 PASS、FAIL 或 UNKNOWN")
    if fact_type not in ALLOWED_FACT_TYPES:
        raise GuardInputError(f"{candidate_label} 使用了未知事实类型：{fact_type}")
    _require_mode_compatible_fact(
        fact_type,
        evidence_mode,
        f"{candidate_label}.checks[{index}]",
    )
    if status in {"PASS", "FAIL"} and not evidence:
        raise GuardInputError(f"{candidate_label} 的 {constraint} 需要证据说明")
    if status == "UNKNOWN" and fact_type != "UNKNOWN":
        raise GuardInputError(f"{candidate_label} 的 {constraint} 待确认时使用 UNKNOWN")
    if status in {"PASS", "FAIL"} and fact_type == "UNKNOWN":
        raise GuardInputError(f"{candidate_label} 的 {constraint} 已判断状态需要已知事实类型")
    if kind == "HARD" and status in {"PASS", "FAIL"} and fact_type not in OBSERVED_FACT_TYPES:
        raise GuardInputError(
            f"{candidate_label} 的硬约束 {constraint} 需要工具、文档或测试观察证据"
        )

    return {
        "constraint_id": constraint_id,
        "constraint": constraint,
        "kind": kind,
        "status": status,
        "fact_type": fact_type,
        "evidence": evidence,
    }


def _analyze_candidates(
    raw_candidates: Any,
    budget_fen: Any,
    evidence_mode: str,
    required_hard_constraints: Sequence[Mapping[str, str]],
    evaluated_at: str,
    expected_fingerprint: str,
) -> dict[str, Any]:
    candidates = _require_list(raw_candidates, "candidates")
    budget = None if budget_fen is None else _require_fen(budget_fen, "draft.budget_fen")
    analyzed: list[dict[str, Any]] = []
    required_constraint_ids = {
        item["id"] for item in required_hard_constraints
    }

    candidate_ids: set[str] = set()
    for index, raw in enumerate(candidates, start=1):
        candidate = _require_mapping(raw, f"candidates[{index}]")
        _reject_unknown_keys(
            candidate,
            {
                "checks",
                "id",
                "name",
                "price_binding",
                "price_evidence",
                "price_fact_type",
                "price_freshness",
                "price_observed_at",
                "price_source_tool",
                "quoted_total_fen",
                "soft_score",
            },
            f"candidates[{index}]",
        )
        candidate_id = _require_text(candidate.get("id"), f"candidates[{index}].id")
        if candidate_id in candidate_ids:
            raise GuardInputError(f"candidates 出现重复 id：{candidate_id}")
        candidate_ids.add(candidate_id)
        name = _require_text(candidate.get("name"), f"candidates[{index}].name")
        total = candidate.get("quoted_total_fen")
        price_fact_type = None
        price_evidence = None
        price_source_tool = None
        price_observed_at = None
        price_freshness = "UNKNOWN"
        price_binding = None
        price_fingerprint = None
        price_binding_status = "UNKNOWN"
        if total is not None:
            total = _require_fen(total, f"candidates[{index}].quoted_total_fen")
            price_fact_type, price_evidence = _require_dynamic_fact(
                candidate.get("price_fact_type"),
                candidate.get("price_evidence"),
                evidence_mode,
                f"candidates[{index}].price",
            )
            price_source_tool = _require_text(
                candidate.get("price_source_tool"),
                f"candidates[{index}].price_source_tool",
            )
            if price_source_tool != "calculate-price":
                raise GuardInputError(
                    f"candidates[{index}].price_source_tool 需要 calculate-price"
                )
            price_observed_at = _require_timestamp(
                candidate.get("price_observed_at"),
                f"candidates[{index}].price_observed_at",
            )
            _require_observed_by(
                price_observed_at,
                evaluated_at,
                f"candidates[{index}].price_observed_at",
            )
            price_freshness = _require_freshness(
                candidate.get("price_freshness"),
                f"candidates[{index}].price_freshness",
            )
            price_binding = _basket_from_binding(
                _require_mapping(
                    candidate.get("price_binding"),
                    f"candidates[{index}].price_binding",
                ),
                f"candidates[{index}].price_binding",
            )
            price_fingerprint = _fingerprint(price_binding)
            price_binding_status = (
                "MATCH"
                if price_fingerprint == expected_fingerprint
                else "MISMATCH"
            )
        else:
            orphan_price_fields = [
                field
                for field in (
                    "price_fact_type",
                    "price_evidence",
                    "price_source_tool",
                    "price_observed_at",
                    "price_freshness",
                    "price_binding",
                )
                if candidate.get(field) is not None
            ]
            if orphan_price_fields:
                raise GuardInputError(
                    f"candidates[{index}] 缺少 quoted_total_fen，价格证据字段需一并留空"
                )
        soft_score = candidate.get("soft_score", 0)
        if not _is_int(soft_score) or soft_score < 0:
            raise GuardInputError(f"candidates[{index}].soft_score 需要非负整数")
        checks = [
            _analyze_check(
                item,
                f"candidates[{index}]",
                check_index,
                evidence_mode,
            )
            for check_index, item in enumerate(
                _require_list(candidate.get("checks", []), f"candidates[{index}].checks"),
                start=1,
            )
        ]
        check_constraints = [item["constraint"] for item in checks]
        duplicate_constraints = sorted(
            constraint
            for constraint, count in Counter(check_constraints).items()
            if count > 1
        )
        if duplicate_constraints:
            raise GuardInputError(
                f"candidates[{index}] 出现重复约束：{'；'.join(duplicate_constraints)}"
            )
        check_ids = [
            item["constraint_id"]
            for item in checks
            if item["constraint_id"] is not None
        ]
        duplicate_ids = sorted(
            constraint_id
            for constraint_id, count in Counter(check_ids).items()
            if count > 1
        )
        if duplicate_ids:
            raise GuardInputError(
                f"candidates[{index}] 出现重复 constraint_id：{'；'.join(duplicate_ids)}"
            )
        for required in required_hard_constraints:
            constraint_id = required["id"]
            constraint = required["user_text"]
            matches = [
                item for item in checks if item["constraint_id"] == constraint_id
            ]
            text_matches = [
                item for item in checks if item["constraint"] == constraint
            ]
            if not matches and text_matches:
                raise GuardInputError(
                    f"candidates[{index}] 的 {constraint} 需要 constraint_id={constraint_id}"
                )
            if matches and matches[0]["constraint"] != constraint:
                raise GuardInputError(
                    f"candidates[{index}] 的 {constraint_id} 需要保留用户原话：{constraint}"
                )
            if matches and matches[0]["kind"] != "HARD":
                raise GuardInputError(
                    f"candidates[{index}] 的排除项 {constraint} 需要 HARD 检查"
                )
            if not matches:
                checks.append(
                    {
                        "constraint_id": constraint_id,
                        "constraint": constraint,
                        "kind": "HARD",
                        "status": "UNKNOWN",
                        "fact_type": "UNKNOWN",
                        "evidence": "",
                    }
                )
        undeclared_hard_checks = [
            item["constraint"]
            for item in checks
            if item["kind"] == "HARD"
            and item["constraint_id"] not in required_constraint_ids
        ]
        if undeclared_hard_checks:
            raise GuardInputError(
                f"candidates[{index}] 的硬约束需要来自 draft.required_constraints："
                + "；".join(undeclared_hard_checks)
            )

        if (
            total is not None
            and price_freshness != "CURRENT"
            and all(item["constraint"] != "价格新鲜度" for item in checks)
        ):
            checks.append(
                {
                    "constraint": "价格新鲜度",
                    "constraint_id": None,
                    "kind": "HARD",
                    "status": "UNKNOWN",
                    "fact_type": "UNKNOWN",
                    "evidence": "",
                }
            )
        if total is None and all(
            item["constraint"] != "价格核验" for item in checks
        ):
            checks.append(
                {
                    "constraint": "价格核验",
                    "constraint_id": None,
                    "kind": "HARD",
                    "status": "UNKNOWN",
                    "fact_type": "UNKNOWN",
                    "evidence": "",
                }
            )

        hard_failures = [
            item["constraint"]
            for item in checks
            if item["kind"] == "HARD" and item["status"] == "FAIL"
        ]
        hard_unknowns = [
            item["constraint"]
            for item in checks
            if item["kind"] == "HARD" and item["status"] == "UNKNOWN"
        ]
        hard_passes = sum(
            item["kind"] == "HARD" and item["status"] == "PASS" for item in checks
        )
        soft_passes = sum(
            item["kind"] == "SOFT" and item["status"] == "PASS" for item in checks
        )

        budget_status = "UNSET" if budget is None else "UNKNOWN"
        if budget is not None and total is not None and price_freshness == "CURRENT":
            budget_status = "WITHIN" if total <= budget else "OVER"
            if budget_status == "OVER":
                hard_failures.append(f"预算超出 {format_fen(total - budget)}")

        eligible = not hard_failures
        decision_status = (
            "CONFLICT"
            if hard_failures
            else "PENDING"
            if hard_unknowns
            else "READY"
        )
        analyzed.append(
            {
                "id": candidate_id,
                "name": name,
                "quoted_total_fen": total,
                "price_fact_type": price_fact_type,
                "price_evidence": price_evidence,
                "price_source_tool": price_source_tool,
                "price_observed_at": price_observed_at,
                "price_freshness": price_freshness,
                "price_binding": (
                    None if price_binding is None else _public_basket(price_binding)
                ),
                "price_binding_status": price_binding_status,
                "soft_score": soft_score,
                "checks": checks,
                "hard_failures": hard_failures,
                "hard_unknowns": hard_unknowns,
                "hard_passes": hard_passes,
                "soft_passes": soft_passes,
                "budget_status": budget_status,
                "eligible": eligible,
                "decision_status": decision_status,
            }
        )

    def ranking_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
        total = (
            candidate["quoted_total_fen"]
            if candidate["price_freshness"] == "CURRENT"
            else None
        )
        return (
            0 if candidate["eligible"] else 1,
            len(candidate["hard_unknowns"]),
            0 if candidate["budget_status"] in {"WITHIN", "UNSET"} else 1,
            -candidate["hard_passes"],
            -candidate["soft_passes"],
            -candidate["soft_score"],
            total if total is not None else 10**18,
            candidate["id"],
        )

    ranked = sorted(analyzed, key=ranking_key)
    recommended = [candidate for candidate in ranked if candidate["eligible"]][:3]
    conflicts = sorted(
        {
            conflict
            for candidate in analyzed
            for conflict in candidate["hard_failures"]
        }
    )
    selection_state = "EMPTY" if not analyzed else "HAS_MATCH" if recommended else "ALL_CONFLICT"
    return {
        "all": ranked,
        "recommended": recommended,
        "conflicts": conflicts,
        "has_match": bool(recommended),
        "selection_state": selection_state,
    }


def _unique_texts(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _item_line(index: int, item: Mapping[str, Any]) -> str:
    options = item["options"]
    option_text = (
        ""
        if not options
        else "（选项：" + "；".join(option["name"] for option in options) + "）"
    )
    return f"{index}. {item['name']} × {item['quantity']}{option_text}"


def _render_quote_card(
    draft: Mapping[str, Any],
    quote: Mapping[str, Any],
    budget: Mapping[str, Any],
    extra_pending: Sequence[str],
) -> str | None:
    if quote["status"] != "VALID" or budget["status"] == "OVER":
        return None

    store_name = quote["binding"]["store_name"]
    store_code = quote["binding"]["store_code"]
    items = quote["binding"]["items"]
    exclusions = _text_list(draft.get("exclusions", []), "draft.exclusions")
    pending = _unique_texts(
        [
            *_text_list(
                draft.get("pending_confirmations", []), "draft.pending_confirmations"
            ),
            *extra_pending,
        ]
    )
    pending_set = set(pending)
    pending_exclusions = [item for item in exclusions if item in pending_set]
    confirmed_exclusions = [item for item in exclusions if item not in pending_set]
    pending = [item for item in pending if item not in set(exclusions)]
    coupon_count = quote["binding"]["coupon_count"]
    lines = [
        "【报价核对｜尚未下单】",
        f"门店：{store_name}（编码：{store_code}）",
        f"取餐方式：{quote['binding']['fulfillment']}",
        "商品与数量：",
    ]
    lines.extend(_item_line(index, item) for index, item in enumerate(items, start=1))
    if confirmed_exclusions:
        lines.append("已确认避开：" + "；".join(confirmed_exclusions))
    if pending_exclusions:
        lines.append("希望避开（待确认）：" + "；".join(pending_exclusions))
    lines.append(
        f"优惠：已按本轮报价绑定 {coupon_count} 项"
        if coupon_count
        else "优惠：保持原样（当前未选择优惠）"
    )
    lines.append(f"应付总额：{format_fen(quote['total_fen'])}")
    lines.append(f"核价时间：{quote['observed_at']}")
    if pending:
        lines.append("请现场确认：" + "；".join(pending))
    lines.append("下一步由你选择：继续修改 / 生成沟通卡 / 转官方渠道")
    return "\n".join(lines)


def _render_communication_card(
    draft: Mapping[str, Any],
    quote: Mapping[str, Any],
    extra_pending: Sequence[str],
) -> str:
    store_name = quote["binding"]["store_name"]
    store_code = quote["binding"]["store_code"]
    items = quote["binding"]["items"]
    exclusions = _text_list(draft.get("exclusions", []), "draft.exclusions")
    pending = _unique_texts(
        [
            *_text_list(
                draft.get("pending_confirmations", []), "draft.pending_confirmations"
            ),
            *extra_pending,
        ]
    )
    pending_set = set(pending)
    pending_exclusions = [item for item in exclusions if item in pending_set]
    confirmed_exclusions = [item for item in exclusions if item not in pending_set]
    pending = [item for item in pending if item not in set(exclusions)]
    lines = [
        "【沟通卡｜请协助核对｜尚未下单】",
        f"门店：{store_name}（编码：{store_code}）",
        f"取餐方式：{quote['binding']['fulfillment']}",
        "我想要：",
    ]
    lines.extend(_item_line(index, item) for index, item in enumerate(items, start=1))
    if confirmed_exclusions:
        lines.append("已确认避开：" + "；".join(confirmed_exclusions))
    if pending_exclusions:
        lines.append("请协助确认并避开：" + "；".join(pending_exclusions))
    coupon_count = quote["binding"]["coupon_count"]
    lines.append(
        f"优惠：已按本轮报价绑定 {coupon_count} 项"
        if coupon_count
        else "优惠：保持原样（当前未选择优惠）"
    )
    if pending:
        lines.append("请协助确认：" + "；".join(pending))
    lines.extend(
        [
            f"当前核价：{format_fen(quote['total_fen'])}",
            f"核价时间：{quote['observed_at']}",
            "核对完成后，请把选择交给食客本人。",
        ]
    )
    return "\n".join(lines)


def _selected_candidate(
    candidates: Mapping[str, Any], selected_id: str | None
) -> Mapping[str, Any] | None:
    if selected_id is None:
        return None
    for candidate in candidates["all"]:
        if candidate["id"] == selected_id:
            return candidate
    raise GuardInputError(f"selected_candidate_id 未找到候选：{selected_id}")


def _handoff_blockers(
    selected: Mapping[str, Any] | None,
    quote: Mapping[str, Any],
    budget: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if selected is None:
        blockers.append("请选择一个候选")
        return blockers
    if selected["hard_failures"]:
        blockers.append("选中候选仍有硬约束冲突")
    if selected["price_binding_status"] != "MATCH":
        blockers.append("选中候选与当前草稿清单待对齐")
    if selected["quoted_total_fen"] != quote["total_fen"]:
        blockers.append("选中候选核价与当前草稿报价待对齐")
    if selected["price_freshness"] != "CURRENT":
        blockers.append("选中候选价格新鲜度待确认")
    if quote["status"] != "VALID":
        blockers.append("当前草稿等待重新核价")
    if budget["status"] == "OVER":
        blockers.append("当前报价高于预算")
    return _unique_texts(blockers)


def analyze_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Analyze one fixture or tool-observed draft and return a structured report."""

    try:
        data = _require_mapping(payload, "payload")
        _reject_unknown_keys(
            data,
            {
                "candidates",
                "card_requested",
                "communication_card_requested",
                "draft",
                "evaluated_at",
                "evidence_mode",
                "offer_comparison",
                "quote",
                "requested_tool",
                "response_mode",
                "selected_candidate_id",
            },
            "payload",
        )
        evidence_mode = _require_text(data.get("evidence_mode"), "evidence_mode")
        if evidence_mode not in ALLOWED_EVIDENCE_MODES:
            raise GuardInputError("evidence_mode 需要 TEST_FIXTURE 或 TOOL_OBSERVED")
        evaluated_at = _require_timestamp(data.get("evaluated_at"), "evaluated_at")
        draft = _require_mapping(data.get("draft"), "draft")
        people = draft.get("people")
        if people is not None and (not _is_int(people) or people < 1):
            raise GuardInputError("draft.people 需要正整数")
        _text_list(draft.get("wants", []), "draft.wants")
        _text_list(draft.get("exclusions", []), "draft.exclusions")
        required_constraints = _required_constraints(draft)
        _text_list(draft.get("pending_confirmations", []), "draft.pending_confirmations")
        expected_fingerprint = _fingerprint(_basket_from_draft(draft))

        quote = _analyze_quote(
            draft, data.get("quote"), evidence_mode, evaluated_at
        )
        budget = _analyze_budget(draft, quote)
        candidates = _analyze_candidates(
            data.get("candidates", []),
            draft.get("budget_fen"),
            evidence_mode,
            required_constraints,
            evaluated_at,
            expected_fingerprint,
        )
        requested_tool = data.get("requested_tool")
        policy = None if requested_tool is None else tool_policy(requested_tool)
        card_requested = _require_bool(
            data.get("card_requested", False), "card_requested"
        )
        communication_card_requested = _require_bool(
            data.get("communication_card_requested", False),
            "communication_card_requested",
        )
        response_mode = _require_text(
            data.get("response_mode", "STANDARD"), "response_mode"
        )
        if response_mode not in ALLOWED_RESPONSE_MODES:
            raise GuardInputError(
                "response_mode 需要 STANDARD 或 SCREEN_READER"
            )
        selected_id = data.get("selected_candidate_id")
        selected_id = (
            None
            if selected_id is None
            else _require_text(selected_id, "selected_candidate_id")
        )
        selected = _selected_candidate(candidates, selected_id)
        blockers = (
            _handoff_blockers(selected, quote, budget)
            if card_requested or communication_card_requested
            else []
        )
        extra_pending = [] if selected is None else selected["hard_unknowns"]
        can_render_cards = not blockers
        quote_card = (
            _render_quote_card(draft, quote, budget, extra_pending)
            if card_requested and can_render_cards
            else None
        )
        communication_card = (
            _render_communication_card(draft, quote, extra_pending)
            if communication_card_requested and can_render_cards
            else None
        )

        state = "DRAFT"
        if quote["status"] == "VALID":
            state = "QUOTED"
        if quote_card is not None or communication_card is not None:
            state = "HANDOFF_READY"

        offer_comparison = None
        if data.get("offer_comparison") is not None:
            offer_input = _require_mapping(data["offer_comparison"], "offer_comparison")
            _reject_unknown_keys(
                offer_input,
                {"alternative", "baseline"},
                "offer_comparison",
            )
            offer_comparison = compare_offers(
                _require_mapping(offer_input.get("baseline"), "offer_comparison.baseline"),
                _require_mapping(
                    offer_input.get("alternative"), "offer_comparison.alternative"
                ),
                evidence_mode,
                evaluated_at,
            )

        return {
            "ok": True,
            "evidence_mode": evidence_mode,
            "evaluated_at": evaluated_at,
            "response_mode": response_mode,
            "state": state,
            "quote": quote,
            "budget": budget,
            "candidates": candidates,
            "requested_tool": requested_tool,
            "tool_policy": policy,
            "offer_comparison": offer_comparison,
            "selected_candidate_id": selected_id,
            "handoff_blockers": blockers,
            "quote_card": quote_card,
            "communication_card": communication_card,
            "errors": [],
        }
    except GuardInputError as error:
        return {
            "ok": False,
            "state": "DRAFT",
            "errors": [str(error)],
        }


def _lines_for_candidate(
    candidate: Mapping[str, Any], position: int
) -> Iterable[str]:
    total = candidate["quoted_total_fen"]
    number_words = {1: "一", 2: "二", 3: "三"}
    yield f"候选{number_words.get(position, position)}。"
    yield f"名称：{candidate['name']}"
    binding = candidate["price_binding"]
    if binding is None:
        yield "数量：待确认"
    else:
        quantity = sum(item["quantity"] for item in binding["items"])
        yield f"数量：共 {quantity} 份"
    if total is not None:
        if candidate["price_freshness"] == "CURRENT":
            yield f"核价：{format_fen(total)}"
        else:
            yield f"历史参考价：{format_fen(total)}；待重新核价"
        yield f"核价时间：{candidate['price_observed_at']}"
    else:
        yield "核价：待取得"
    confirmed = [
        item["constraint"]
        for item in candidate["checks"]
        if item["status"] == "PASS"
    ]
    yield "已确认：" + ("；".join(confirmed) if confirmed else "当前 0 项")
    if candidate["hard_unknowns"]:
        yield "待确认：" + "；".join(candidate["hard_unknowns"])
    else:
        yield "待确认：当前 0 项"
    yield "选择依据：" + (
        f"硬约束已确认 {candidate['hard_passes']} 项，"
        f"软偏好已确认 {candidate['soft_passes']} 项"
    )
    yield f"你可以说：选{number_words.get(position, position)}、听详情、换一批、暂时结束。"


def _comparison_item(item: Mapping[str, Any]) -> str:
    options = item["options"]
    option_text = "" if not options else "（选项：" + "；".join(options) + "）"
    return f"{item['name']} × {item['quantity']}{option_text}"


def render_text_report(report: Mapping[str, Any]) -> str:
    """Render a short screen-reader-friendly report from ``analyze_payload``."""

    if not report.get("ok"):
        errors = report.get("errors", ["输入仍待确认"])
        return "【慢慢点本地护栏报告】\n状态：DRAFT\n待核对：" + "；".join(errors)

    lines = [
        f"【慢慢点本地护栏报告｜{report['evidence_mode']}】",
        f"回应模式：{report.get('response_mode', 'STANDARD')}",
        f"当前状态：{report['state']}",
        f"报价状态：{report['quote']['status']}",
        f"预算状态：{report['budget']['status']}",
    ]
    if report.get("requested_tool"):
        lines.append(
            f"工具路线：{report['requested_tool']} → {report['tool_policy']}"
        )
    if report["quote"].get("display_deltas"):
        lines.append(
            "展示名采用本轮核价回执："
            + "；".join(report["quote"]["display_deltas"])
        )

    recommended = report["candidates"]["recommended"]
    if recommended:
        lines.append("最多三个候选：")
        for position, candidate in enumerate(recommended, start=1):
            lines.extend(_lines_for_candidate(candidate, position))
    elif report["candidates"]["selection_state"] == "EMPTY":
        lines.append("当前还没有候选。先查询门店菜单，再生成候选。")
    else:
        lines.append("当前候选与硬约束存在冲突。")
        conflicts = report["candidates"]["conflicts"]
        if conflicts:
            lines.append("冲突项：" + "；".join(conflicts))
        lines.append("由你选择：保留原要求并换一批 / 调整一项 / 暂时结束")

    comparison = report.get("offer_comparison")
    if comparison:
        lines.append(f"优惠比较：{comparison['comparison_type']}")
        comparison_type = comparison["comparison_type"]
        spend_change = comparison["spend_change_fen"]
        if comparison_type == "EQUIVALENT_BASKET":
            if spend_change < 0:
                lines.append("同一清单节省：" + format_fen(-spend_change))
            elif spend_change == 0:
                lines.append(
                    "同一清单总额持平："
                    + format_fen(comparison["alternative_total_fen"])
                )
            else:
                lines.append("同一清单多花：" + format_fen(spend_change))
        else:
            lines.append(
                "基准总额：" + format_fen(comparison["baseline_total_fen"])
            )
            lines.append(
                "方案总额：" + format_fen(comparison["alternative_total_fen"])
            )
            if spend_change < 0:
                lines.append("金额变化：少花 " + format_fen(-spend_change))
            elif spend_change == 0:
                lines.append("金额变化：持平")
            else:
                lines.append("金额变化：多花 " + format_fen(spend_change))
            if comparison["context_changes"]:
                lines.append("场景变化：" + "；".join(comparison["context_changes"]))
            if comparison["added"]:
                lines.append(
                    "增加项："
                    + "；".join(_comparison_item(item) for item in comparison["added"])
                )
            if comparison["removed"]:
                lines.append(
                    "减少项："
                    + "；".join(_comparison_item(item) for item in comparison["removed"])
                )
            if comparison["same_name_transaction_change"]:
                lines.append(
                    "同名商品的交易项发生变化，请在官方详情中核对具体内容。"
                )
            if comparison_type == "STALE_EVIDENCE":
                lines.append("报价新鲜度待核实，完成重核后再比较金额。")
            elif comparison_type == "DIFFERENT_CONTEXT":
                lines.append("两个方案分属各自场景，以上金额并列展示。")
            elif comparison_type == "DIFFERENT_PRICING_REQUEST":
                lines.append(
                    "两份核价请求含各自条件，以上金额并列展示，完成同基准核价后再计算节省。"
                )
            else:
                lines.append("清单发生变化，由食客判断新增或减少内容的价值。")
        if comparison["coupon_selection_changed"]:
            lines.append(
                "优惠差异：基准 "
                + str(comparison["baseline_coupon_count"])
                + " 项｜方案 "
                + str(comparison["alternative_coupon_count"])
                + " 项"
            )
        if comparison["pricing_request_changed"]:
            lines.append(
                "核价请求摘要有变化：请结合优惠、权益、餐具与套餐细节一并核对。"
            )

    blockers = report.get("handoff_blockers", [])
    if blockers:
        lines.append("交接卡等待完成：" + "；".join(blockers))

    if report.get("quote_card"):
        lines.extend(["", report["quote_card"]])
    if report.get("communication_card"):
        lines.extend(["", report["communication_card"]])
    return "\n".join(lines)
