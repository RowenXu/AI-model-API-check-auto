#!/usr/bin/env python3
"""
API Quota Monitor — Main Entry Point
Collects remaining quota/balance from multiple LLM providers and writes
a unified JSON report + GitHub Actions Job Summary.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from providers.openai_provider   import OpenAIProvider
from providers.copilot_provider  import CopilotProvider
from providers.aliyun_provider   import AliyunProvider
from providers.kimi_provider     import KimiProvider
from providers.deepseek_provider import DeepSeekProvider
from providers.mimo_provider     import MiMoProvider
from providers.zai_provider      import ZaiProvider

REPORT_PATH = Path(__file__).parent.parent / "data" / "quota_report.json"

PROVIDERS = [
    OpenAIProvider,
    CopilotProvider,
    AliyunProvider,
    KimiProvider,
    DeepSeekProvider,
    MiMoProvider,
    ZaiProvider,
]


def collect_all() -> dict:
    results = []
    for cls in PROVIDERS:
        p = cls()
        print(f"[→] Collecting: {p.name} ...", flush=True)
        try:
            data = p.collect()
            data["status"] = "ok"
            print(f"[✓] {p.name}: {p.summary(data)}")
        except Exception as exc:
            data = {"status": "error", "error": str(exc)}
            print(f"[✗] {p.name}: {exc}", file=sys.stderr)
        data["provider"] = p.name
        results.append(data)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "providers": results,
    }


def write_report(report: dict):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n[✓] Report saved → {REPORT_PATH}")


def write_job_summary(report: dict):
    """Write a Markdown table to GitHub Actions Job Summary."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    ts = report["generated_at"]
    lines = [
        "## 💰 API Quota Report",
        f"> Generated at: `{ts}`\n",
        "| Provider | Status | Balance / Quota | Unit | Note |",
        "|---|---|---|---|---|",
    ]
    for p in report["providers"]:
        status = "✅" if p["status"] == "ok" else "❌"
        name   = p.get("provider", "—")
        bal    = p.get("display_balance", "N/A")
        unit   = p.get("unit", "—")
        note   = p.get("note", "")
        lines.append(f"| {name} | {status} | {bal} | {unit} | {note} |")

    if any(p["status"] == "error" for p in report["providers"]):
        lines.append("\n### ⚠️ Errors")
        for p in report["providers"]:
            if p["status"] == "error":
                lines.append(f"- **{p['provider']}**: `{p.get('error', 'unknown')}`")

    with open(summary_path, "w") as f:
        f.write("\n".join(lines))
    print("[✓] Job Summary written.")


if __name__ == "__main__":
    report = collect_all()
    write_report(report)
    write_job_summary(report)
    if any(p["status"] == "error" for p in report["providers"]):
        sys.exit(1)
