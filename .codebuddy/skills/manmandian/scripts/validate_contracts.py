from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
SKILL_DIR = REPO / ".codebuddy" / "skills" / "manmandian"
CONTRACTS = SKILL_DIR / "references" / "mcd-tool-contracts.json"
ROUTER = SKILL_DIR / "references" / "mcd-tool-router.md"
MATRIX = REPO / "docs" / "MCP_CAPABILITY_MATRIX.md"
README = REPO / "README.md"

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

    requirements = json.loads(text(REPO / "requirements.lock.json"))["requirements"]
    check(sum(item["id"] == "R23" for item in requirements) == 1, "R23 requirement entry")

    declaration = (REPO / "CONTEST_DECLARATION.md").read_bytes().replace(b"\r\n", b"\n")
    git_blob = hashlib.sha1(
        b"blob " + str(len(declaration)).encode("ascii") + b"\0" + declaration
    ).hexdigest()
    check(git_blob == "136e76f3160317049f19f5ba03f4d0fedd70fc3c", "official declaration blob")


def main() -> int:
    validate_contracts()
    validate_docs()
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
