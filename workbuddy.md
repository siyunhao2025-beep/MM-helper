# WorkBuddy 开发上下文（workbuddy.md）

> **声明**：本文件当前为**摘要版**（已明确标注），不是完整原始对话导出。本项目真实使用 WorkBuddy（腾讯）开发；完整上下文导出待作者在 WorkBuddy 客户端操作后替换本文件。摘要内容全部来自真实开发过程，已脱敏（不含 Token、电话、地址、支付信息）。

## 开发环境（真实）

- 工具：WorkBuddy 桌面版（官方比赛合作工具）
- 时间线：2026-10-09 起，最新记录 2026-10-10
- 已连接麦当劳官方 MCP（mcd.cn；凭证保存在本地受保护配置，从未进入仓库、日志或本文件）

## 真实开发记录（节选，均可对账）

- 2026-10-09 15:34 — 真实调用 query-my-account（traceId f2a5c0be25b8b87ee1289978062e426d），确认账户积分状态
- 2026-10-09 17:05 — 真实只读链五环调用：query-nearby-stores / query-meals / query-meal-detail / query-store-coupons / calculate-price（traceId 见 docs/EVIDENCE_LEDGER.jsonl E2–E6）
- 2026-10-09 17:35 — 核验官方仓库 M-China/mcd-developer-innovation-challenge 的 README.md / activityGuidelines.md / CONTEST_DECLARATION.md（来源登记现位于 `.codebuddy/skills/manmandian-builder/references/sources.md`）
- 2026-10-09 17:45 — 本仓库 P0 建档推送（治理文件、官方声明原文、MCP 集成说明、能力矩阵、证据台账）
- 2026-10-10 11:14 — 在 WorkBuddy 中导出 mcd-mcp 的 35 项注入式工具定义，产物含 raw JSON、catalog JSONL、能力矩阵、采集报告与 SHA-256 清单；本次专门采集元数据，业务调用和状态变更调用均为 0
- 2026-10-10 — 独立复核 35 个名称、描述、输入 Schema 与哈希，并将脱敏契约、八条任务路线和 7 项状态变更门控写入运行 Skill；证据见 E18

## 需求来源

完整开发规范见主提示词《慢慢点 WorkBuddy 完整执行提示词（单文件整合版 v1.0）》（用户提供，SHA-256 658b016c…c2fa6）。
