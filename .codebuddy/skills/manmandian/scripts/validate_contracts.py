from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
SKILL_DIR = REPO / ".codebuddy" / "skills" / "manmandian"
CONTRACTS = SKILL_DIR / "references" / "mcd-tool-contracts.json"
ROUTER = SKILL_DIR / "references" / "mcd-tool-router.md"
DECISION_CONTRACT = SKILL_DIR / "references" / "decision-contract.md"
ACCESSIBLE_MODES = SKILL_DIR / "references" / "accessible-response-modes.md"
MATRIX = REPO / "docs" / "MCP_CAPABILITY_MATRIX.md"
README = REPO / "README.md"
WORKBUDDY = REPO / "workbuddy.md"
THIRD_PARTY = REPO / "THIRD_PARTY_NOTICES.md"
LICENSE = REPO / "LICENSE"
STATUS = REPO / "PROJECT_STATUS.md"
KNOWN_LIMITATIONS = REPO / "docs" / "KNOWN_LIMITATIONS.md"
FILE_MAP = REPO / "docs" / "FILE_MAP.md"
HANDOFF = REPO / "CONTEXT_HANDOFF.md"
DECISIONS = REPO / "DECISIONS.md"
BUILDER_SOURCES = REPO / ".codebuddy" / "skills" / "manmandian-builder" / "references" / "sources.md"
BUILDER_DELIVERY = REPO / ".codebuddy" / "skills" / "manmandian-builder" / "references" / "delivery.md"
REQUIREMENTS = REPO / "requirements.lock.json"
EVIDENCE = REPO / "docs" / "EVIDENCE_LEDGER.jsonl"
CORE = REPO / "src" / "core" / "decision_guard.py"
CORE_CLI = REPO / "src" / "core" / "cli.py"
FIXTURE = REPO / "examples" / "accessible-order.fixture.json"
UNIT_TESTS = REPO / "tests" / "test_decision_guard.py"

EXPECTED_NAMES = {
    "auto-bind-coupons",
    "available-coupons",
    "calculate-price",
    "campaign-calendar",
    "cancel-order",
    "create-order",
    "delivery-create-address",
    "delivery-query-addresses",
    "delivery-query-stores",
    "draw-lottery",
    "list-nutrition-foods",
    "mall-create-order",
    "mall-order-detail",
    "mall-order-list",
    "mall-points-products",
    "mall-product-detail",
    "now-time-info",
    "order-list",
    "party-order-create",
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

WRITE_NAMES = {
    "auto-bind-coupons",
    "cancel-order",
    "create-order",
    "delivery-create-address",
    "draw-lottery",
    "mall-create-order",
    "party-order-create",
}

PUBLIC_MARKDOWN = [
    README,
    SKILL_DIR / "SKILL.md",
    REPO / "MCP_INTEGRATION.md",
    ROUTER,
    DECISION_CONTRACT,
    ACCESSIBLE_MODES,
    WORKBUDDY,
    THIRD_PARTY,
]

NEGATIVE_EN = re.compile(
    r"\b(no|not|never|none|cannot|can.t|don.t|doesn.t|won.t|without)\b",
    re.IGNORECASE,
)

PROVIDER_EXAMPLES = [
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    re.compile(r"1030108270000795607354880945"),
    re.compile(r"北京市东城区"),
    re.compile(r"郑化"),
]


failures: list[str] = []
checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(label)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def schema_hash(value: object) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def all_keys(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from all_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_keys(child)


def validate_contracts() -> None:
    payload = json.loads(text(CONTRACTS))
    tools = payload["tools"]
    names = [item["short_name"] for item in tools]
    runtime_names = [item["runtime_name"] for item in tools]

    check(payload["format_version"] == "1.1", "contract format_version")
    check(payload["snapshot"]["tool_count"] == 35, "snapshot tool_count")
    check(payload["snapshot"]["business_tool_invocations"] == 0, "snapshot business calls")
    check(payload["snapshot"]["state_change_invocations"] == 0, "snapshot state calls")
    check(len(names) == 35, "contract row count")
    check(len(set(names)) == 35, "unique short names")
    check(len(set(runtime_names)) == 35, "unique runtime names")
    check(set(names) == EXPECTED_NAMES, "exact 35-name inventory")
    check(
        all(name == f"mcp__mcd-mcp__{short}" for name, short in zip(runtime_names, names)),
        "runtime name prefix",
    )

    writes = {
        item["short_name"]
        for item in tools
        if item["side_effect_class"] != "NONE_OBSERVED"
    }
    check(writes == WRITE_NAMES, "exact seven state-changing tools")
    check(len(tools) - len(writes) == 28, "28 read/time/calculation tools")

    check(
        all(schema_hash(item["input_schema"]) == item["sanitized_schema_sha256"] for item in tools),
        "sanitized schema hashes",
    )
    check(
        all(re.fullmatch(r"[0-9a-f]{64}", item["source_schema_sha256"]) for item in tools),
        "source schema hash format",
    )
    removed = {"description", "example", "examples", "$comment"}
    check(
        all(removed.isdisjoint(set(all_keys(item["input_schema"]))) for item in tools),
        "provider prose and examples removed from schemas",
    )

    raw = text(CONTRACTS)
    check(all(pattern.search(raw) is None for pattern in PROVIDER_EXAMPLES), "provider example scan")


def validate_docs() -> None:
    router = text(ROUTER)
    matrix = text(MATRIX)
    for name in EXPECTED_NAMES:
        marker = f"`{name}`"
        check(marker in router, f"router contains {name}")
        check(marker in matrix, f"matrix contains {name}")

    skill_lines = text(SKILL_DIR / "SKILL.md").splitlines()
    check(len(skill_lines) < 500, "SKILL.md stays below 500 lines")

    for path in PUBLIC_MARKDOWN:
        value = text(path)
        check("不" not in value, f"affirmative Chinese wording: {path.relative_to(REPO)}")
        check(NEGATIVE_EN.search(value) is None, f"affirmative English wording: {path.relative_to(REPO)}")

    current_state_docs = [STATUS, KNOWN_LIMITATIONS, FILE_MAP, HANDOFF, BUILDER_SOURCES, BUILDER_DELIVERY]
    stale_state_markers = [
        "LICENSE 未添加",
        "LICENSE 未选择",
        "LICENSE | 待作者确认",
        "workbuddy.md 为摘要版",
        "workbuddy.md 仍为摘要版",
        "⚠️ 摘要版",
    ]
    for path in current_state_docs:
        value = text(path)
        check(
            all(marker not in value for marker in stale_state_markers),
            f"current state is synchronized: {path.relative_to(REPO)}",
        )

    project_facts = "\n".join(
        text(path)
        for path in [README, WORKBUDDY, THIRD_PARTY, STATUS, HANDOFF, FILE_MAP, DECISIONS, EVIDENCE]
    )
    check("mcp.cn" not in project_facts, "official MCP hostname is mcp.mcd.cn")
    check("四张 SVG 信息图" not in text(README), "README says five SVG infographics")
    check("四张卡通插画由 OpenAI" in text(README), "README says four generated illustrations")
    check("五张 SVG 信息图" in text(README), "README says five SVG infographics explicitly")

    license_text = text(LICENSE)
    check(license_text.startswith("MIT License\n"), "standard MIT heading")
    check("Copyright (c) 2026 siyunhao2025-beep" in license_text, "MIT copyright line")
    check("依法享有授权权利的原创贡献" in text(THIRD_PARTY), "license scope uses rights-qualified wording")

    workbuddy = text(WORKBUDDY)
    check("结构化公开索引" in workbuddy, "workbuddy artifact shape is explicit")
    check("原生对话上下文" in workbuddy, "workbuddy native export action is explicit")
    check("`README.md` 中三处许可证状态" in workbuddy, "workbuddy records three README updates")
    check("raw 与 catalog 名称一致 | 35 / 35" in workbuddy, "workbuddy name alignment row")
    check("raw 与 catalog 描述一致 | 35 / 35" in workbuddy, "workbuddy description alignment row")
    check("raw 与 catalog `inputSchema` 一致 | 35 / 35" in workbuddy, "workbuddy schema alignment row")

    evidence_text = text(EVIDENCE)
    check("availablePoint=0" not in evidence_text, "public evidence omits exact account points")
    check('"source":"mcp.mcd.cn query-my-account"' in evidence_text, "evidence uses official MCP hostname")

    check("756b6952cd67d35e77d1f237ca2708ff731ea04c" in text(BUILDER_SOURCES), "current challenge commit recorded")
    check("e693168f73634717491890fe4583d4aeb501fb25" in text(BUILDER_SOURCES), "current challenge README blob recorded")
    check("136e76f3160317049f19f5ba03f4d0fedd70fc3c" in text(BUILDER_SOURCES), "official declaration blob recorded")

    readme = text(README)
    check(readme.count("<details>") == readme.count("</details>"), "README details pairs")
    image_sources = re.findall(r'<img\s+[^>]*src="([^"]+)"', readme)
    image_alts = re.findall(r'<img\s+[^>]*alt="([^"]+)"', readme)
    check(len(image_sources) == 9, "README visual entry count")
    check(len(image_alts) == len(image_sources), "README image alt count")
    check(all((REPO / source).exists() for source in image_sources), "README image paths")

    links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", readme)
    local_links = [
        value
        for value in links
        if re.match(r"^(https?://|mailto:|#)", value) is None
    ]
    resolved = [REPO / urllib.parse.unquote(value.split("#", 1)[0]) for value in local_links]
    check(all(path.exists() for path in resolved), "README local links")
    check("flowchart LR" in readme, "README decision flow")
    check("66 项 fixture 自动测试通过" in readme, "README fixture result")
    check("不" not in text(CORE), "affirmative Chinese wording: src/core/decision_guard.py")
    check("不" not in text(CORE_CLI), "affirmative Chinese wording: src/core/cli.py")


def validate_decision_guard() -> None:
    required = [DECISION_CONTRACT, ACCESSIBLE_MODES, CORE, CORE_CLI, FIXTURE, UNIT_TESTS]
    for path in required:
        check(path.exists() and path.stat().st_size > 0, f"decision artifact: {path.relative_to(REPO)}")

    fixture = json.loads(text(FIXTURE))
    check(fixture.get("evidence_mode") == "TEST_FIXTURE", "fixture evidence mode")
    check(fixture.get("response_mode") == "SCREEN_READER", "fixture response mode")
    check(bool(fixture.get("evaluated_at")), "fixture evaluation time")
    check(fixture.get("selected_candidate_id") == "A", "fixture selected candidate")
    quote = fixture.get("quote", {})
    check(quote.get("fact_type") == "TEST_OBSERVED", "fixture quote fact type")
    check(bool(quote.get("evidence")), "fixture quote evidence")
    candidates = fixture.get("candidates", [])
    check(len(candidates) >= 3, "fixture candidate coverage")
    check(
        all(
            item.get("quoted_total_fen") is None
            or (
                item.get("price_fact_type") == "TEST_OBSERVED"
                and bool(item.get("price_evidence"))
                and item.get("price_source_tool") == "calculate-price"
                and item.get("price_freshness") == "CURRENT"
                and bool(item.get("price_binding"))
            )
            for item in candidates
        ),
        "fixture candidate price evidence",
    )
    pricing_hashes = [
        fixture.get("draft", {}).get("pricing_request_sha256"),
        quote.get("binding", {}).get("pricing_request_sha256"),
        *[
            item.get("price_binding", {}).get("pricing_request_sha256")
            for item in candidates
            if item.get("quoted_total_fen") is not None
        ],
        *[
            item.get("pricing_request_sha256")
            for item in fixture.get("offer_comparison", {}).values()
        ],
        *[
            item.get("pricing_basis_sha256")
            for item in fixture.get("offer_comparison", {}).values()
        ],
    ]
    check(
        all(
            isinstance(value, str)
            and re.fullmatch(r"[0-9a-f]{64}", value) is not None
            for value in pricing_hashes
        ),
        "fixture exact pricing-request digests",
    )
    check(
        quote.get("binding", {}).get("store_name")
        and all(
            item.get("price_binding", {}).get("store_name")
            for item in candidates
            if item.get("quoted_total_fen") is not None
        ),
        "fixture store display names",
    )

    core = text(CORE)
    for marker in [
        "GUIDE_ONLY_TOOLS",
        "READ_TOOLS",
        "TEST_FIXTURE",
        "TOOL_OBSERVED",
        "EQUIVALENT_BASKET",
        "CHANGED_BASKET",
        "binding_status",
        "verified_saving_fen",
        "selected_candidate_id",
        "price_binding_status",
        "display_deltas",
        "communication_card",
        "SCREEN_READER",
        "pricing_request_sha256",
        "pricing_request_changed",
        "FULFILLMENT_LABELS",
        "DIFFERENT_PRICING_REQUEST",
    ]:
        check(marker in core, f"decision core contains {marker}")
    check(
        all(name in core for name in WRITE_NAMES),
        "decision core contains seven state-changing tools",
    )
    check(
        all(name in core for name in EXPECTED_NAMES),
        "decision core contains exact 35-tool allowlist",
    )
    check(
        all(marker not in core for marker in ["import requests", "import urllib", "import socket"]),
        "decision core has no network dependency",
    )
    runtime_skill = text(SKILL_DIR / "SKILL.md")
    accessible_modes = text(ACCESSIBLE_MODES)
    requirements_text = text(REQUIREMENTS)
    readme = text(README)
    check(
        all(
            marker in content
            for marker, content in [
                ("【报价核对｜尚未下单】", runtime_skill),
                ("【沟通卡｜请协助核对｜尚未下单】", runtime_skill),
                ("【沟通卡｜请协助核对｜尚未下单】", accessible_modes),
                ("【沟通卡｜请协助核对｜尚未下单】", readme),
                ("希望避开（待确认）", core),
                ("希望避开（待确认）", runtime_skill),
                ("请协助确认并避开", core),
                ("请协助确认并避开", accessible_modes),
                ("官方回执摘要", requirements_text),
            ]
        ),
        "card templates and handoff scope stay synchronized",
    )

    tests = text(UNIT_TESTS)
    test_count = len(re.findall(r"^\s+def test_", tests, flags=re.MULTILINE))
    check(test_count == 66, "decision guard unit-test inventory")
    check("display_name_change" in tests, "display name binding regression")
    check("live_mode_rejects_fixture" in tests, "fixture/live isolation regression")
    check("screen_reader_candidates_are_numbered" in tests, "screen-reader regression")
    check("surrogate_character_is_rejected" in tests, "text injection regression")
    check("complete_delivery_profile_can_be_bound" in tests, "fulfillment profile regression")
    check("pricing_request_hash_requires_sha256" in tests, "pricing request digest regression")
    check("pricing_request_change_is_visible" in tests, "pricing request comparison regression")
    check("candidate_cannot_invent_hard_checks" in tests, "declared hard-constraint regression")
    check("unknown_key_cannot_inject" in tests, "mapping-key injection regression")
    check("hidden_pricing_request_change" in tests, "hidden pricing-request regression")
    check("drive_through_and_group_delivery" in tests, "four-profile fulfillment regression")
    check(
        "minimum_public_details" in tests
        and 'self.assertNotIn("FIXTURE_EXTRA"' in tests
        and 'self.assertNotIn("FIXTURE_DRINK_WARM", render_text_report(report))' in tests
        and "same_name_transaction_change" in tests
        and 'name = _require_text(item.get("name"),' in core,
        "public identifier minimization regression",
    )
    check("store_display_name_comes_from_current_quote" in tests, "store display binding regression")

    unit_result = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    unit_output = unit_result.stdout + unit_result.stderr
    check(
        unit_result.returncode == 0 and "Ran 66 tests" in unit_output,
        "decision guard unit tests execute",
    )

    cli_result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "src.core.cli",
            str(FIXTURE.relative_to(REPO)),
            "--json",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    try:
        cli_payload = json.loads(cli_result.stdout) if cli_result.returncode == 0 else {}
    except json.JSONDecodeError:
        cli_payload = {}
    check(
        cli_payload.get("ok") is True
        and cli_payload.get("state") == "HANDOFF_READY"
        and cli_payload.get("communication_card"),
        "decision guard CLI executes",
    )


def validate_svg() -> None:
    svg_paths = sorted((REPO / "assets").glob("*.svg"))
    check(len(svg_paths) == 5, "SVG count")
    for path in svg_paths:
        root = ET.parse(path).getroot()
        check(root.attrib.get("viewBox") == "0 0 1600 900", f"16:9 viewBox: {path.name}")
        visible_text = " ".join(root.itertext())
        check("不" not in visible_text, f"affirmative SVG Chinese: {path.name}")
        check(NEGATIVE_EN.search(visible_text) is None, f"affirmative SVG English: {path.name}")


def validate_evidence_and_declaration() -> None:
    ledger = [
        json.loads(line)
        for line in text(REPO / "docs" / "EVIDENCE_LEDGER.jsonl").splitlines()
        if line.strip()
    ]
    check(sum(item["id"] == "E18" for item in ledger) == 1, "E18 evidence entry")
    check(sum(item["id"] == "E20" for item in ledger) == 1, "E20 evidence entry")
    check(sum(item["id"] == "E21" for item in ledger) == 1, "E21 evidence entry")
    check(sum(item["id"] == "E22" for item in ledger) == 1, "E22 evidence entry")
    check(sum(item["id"] == "E23" for item in ledger) == 1, "E23 evidence entry")
    e24 = [item for item in ledger if item["id"] == "E24"]
    check(
        len(e24) == 1
        and e24[0].get("fact") == "TEST_OBSERVED"
        and "215/215" in e24[0].get("result", ""),
        "E24 final evidence entry",
    )

    requirements = json.loads(text(REQUIREMENTS))["requirements"]
    check(sum(item["id"] == "R23" for item in requirements) == 1, "R23 requirement entry")
    check(sum(item["id"] == "R24" for item in requirements) == 1, "R24 requirement entry")
    check(sum(item["id"] == "R25" for item in requirements) == 1, "R25 requirement entry")
    check(sum(item["id"] == "R26" for item in requirements) == 1, "R26 requirement entry")

    declaration = (REPO / "CONTEST_DECLARATION.md").read_bytes().replace(b"\r\n", b"\n")
    git_blob = hashlib.sha1(
        b"blob " + str(len(declaration)).encode("ascii") + b"\0" + declaration
    ).hexdigest()
    check(git_blob == "136e76f3160317049f19f5ba03f4d0fedd70fc3c", "official declaration blob")


def main() -> int:
    validate_contracts()
    validate_docs()
    validate_decision_guard()
    validate_svg()
    validate_evidence_and_declaration()

    if failures:
        print(f"FAILED: {len(failures)} of {checks} checks")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PASS: {checks} checks")
    print("35 tools = 28 read/time/calculation + 7 GUIDE_ONLY state changes")
    print("Public wording, links, SVGs, evidence, and declaration are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
