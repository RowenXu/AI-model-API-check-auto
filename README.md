# 💰 AI Model API Quota Monitor

Automated monitoring of remaining API credits/quota across multiple LLM providers, powered by **GitHub Actions**.

## Supported Providers

| Provider | Method | Unit |
|---|---|---|
| OpenAI (ChatGPT / Codex) | Semi-official billing API | USD |
| GitHub Copilot | ✅ Official REST API | Seats |
| 阿里云百炼 (DashScope) | Aliyun BSS OpenAPI | CNY |
| Kimi (Moonshot) | ✅ Official balance API | CNY |
| DeepSeek | ✅ Official balance API | CNY |
| 小米 MiMo | Probe method (no public API) | CNY |
| Z.ai (智谱AI) | Probe + undocumented endpoint | CNY |

## How it works

1. GitHub Actions runs on a **daily schedule** (09:00 CST) or manually via `workflow_dispatch`
2. Each provider's quota/balance is collected via API or probe request
3. Results are saved to `data/quota_report.json` and committed back to the repo
4. A summary table is written to the **Actions Job Summary** page

## Setup

### 1. Add Repository Secrets

Go to `Settings → Secrets and variables → Actions → New repository secret` and add:

| Secret Name | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (`sk-...`) |
| `GH_COPILOT_TOKEN` | PAT with `manage_billing:copilot` scope |
| `GH_COPILOT_ORG` | Your GitHub organization name |
| `ALIYUN_ACCESS_KEY_ID` | Aliyun RAM user AccessKey ID |
| `ALIYUN_ACCESS_KEY_SECRET` | Aliyun RAM user AccessKey Secret (needs `AliyunBSSReadOnlyAccess`) |
| `KIMI_API_KEY` | Kimi / Moonshot API key |
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `MIMO_API_KEY` | Xiaomi MiMo API key |
| `ZAI_API_KEY` | Z.ai API key |

> **Security**: API keys are stored as encrypted GitHub Secrets and are **never** exposed in code or logs.

### 2. Trigger the workflow

- **Automatic**: runs every day at 09:00 CST
- **Manual**: go to `Actions → 💰 API Quota Monitor → Run workflow`

## Output

### `data/quota_report.json`

Auto-generated and committed after every run.

### Actions Job Summary

A formatted Markdown table is written to each run's Job Summary page, visible in the Actions tab.

## Notes

- **小米 MiMo** and **Z.ai** do not expose a public balance API — a minimal probe request (1 token) is sent to verify availability and read rate-limit headers.
- **阿里云百炼** free token quota is only visible in the console; the BSS API returns the overall CNY account balance.
- **OpenAI** billing endpoints are semi-official and may change without notice.
- **GitHub Copilot** reports seat counts, not API call quotas.
