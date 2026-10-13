"""Command-line entry point for the local ManManDian decision guard."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .decision_guard import analyze_payload, render_text_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="检查慢慢点草稿、候选、报价绑定与引导模式。"
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON 输入文件")
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出机器可读 JSON；默认输出读屏友好文字",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"读取输入失败：{error}")
        return 2

    report = analyze_payload(payload)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_text_report(report))
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
