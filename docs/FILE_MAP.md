# FILE_MAP — 文件地图

> 勾选=已存在于仓库且非空；「待建」不算完成。更新于 2026-10-10（P0.9）。

## 根目录

| 路径 | 用途 | 状态 |
|---|---|---|
| README.md | 视觉叙事版项目介绍/诗歌/35 工具地图/真实状态/安装/使用/合规/上传 | ✅ 9 个视觉入口（2026-10-10） |
| CONTEST_DECLARATION.md | 官方参赛声明（原文） | ✅ |
| MCP_INTEGRATION.md | MCP 集成说明（比赛必交） | ✅ |
| mcp-config.example.json | 脱敏配置示例 | ✅ |
| workbuddy.md | WorkBuddy 结构化公开索引 | ⚠️ 索引已建；专项奖励前待作者放入原生对话导出并脱敏对账 |
| .gitignore | 屏蔽密钥/日志/原始媒体 | ✅ |
| PROJECT_CONSTITUTION.md | 项目宪法 | ✅ |
| requirements.lock.json | R01–R24 需求锁定 | ✅ |
| PROJECT_STATUS.md | 当前状态 | ✅ |
| DECISIONS.md | 决定记录 | ✅ |
| CONTEXT_HANDOFF.md | 交接入口 | ✅ |
| THIRD_PARTY_NOTICES.md | 第三方许可与视觉资产来源 | ✅（4 PNG + 5 SVG 已登记） |
| LICENSE | 作者原创贡献许可 | ✅ 标准 MIT；公开署名待作者确认 |

## .codebuddy/

| 路径 | 用途 | 状态 |
|---|---|---|
| rules/manmandian.md | 短规则（主提示词 13.3 原文） | ✅ |
| CODEBUDDY.md | 恢复入口（已观察被客户端自动加载，见 E7） | ✅ |
| skills/manmandian-builder/SKILL.md | 开发 Skill | ✅ |
| skills/manmandian-builder/references/ | truth-and-scope / sources / delivery | ✅×3 |
| skills/manmandian/SKILL.md | 运行 Skill（顾客点餐） | ✅ |
| skills/manmandian/scripts/validate_contracts.py | 35 项契约、语言、链接、SVG、证据、许可证、状态一致性与官方声明零依赖校验 | ✅ |
| skills/manmandian/references/mcd-tool-router.md | 35 项工具的人类可读路由、门控与依赖 | ✅ |
| skills/manmandian/references/mcd-tool-contracts.json | 35 项脱敏输入契约与快照哈希 | ✅ |

## docs/

| 路径 | 状态 |
|---|---|
| MCP_CAPABILITY_MATRIX.md | ✅ |
| EVIDENCE_LEDGER.jsonl | ✅ |
| FILE_MAP.md | ✅（本文件） |
| KNOWN_LIMITATIONS.md | ✅ |
| SOURCE_REGISTER.md | 未单独建文件；来源登记位于 `.codebuddy/skills/manmandian-builder/references/sources.md`（含当前 SHA/版本） |
| FEATURE_STATUS.md / ACCESSIBILITY.md / ACCESSIBILITY_TEST_REPORT.md / SIGN_LANGUAGE_MODEL_CARD.md / DATA_AND_CONSENT.md / TEST_REPORT.md / USER_VALUE_EVALUATION.md / DEMO_SCRIPT.md / SUBMISSION_CHECKLIST.md | 待建（按阶段） |

## src/、tests/ 与 assets/

- PNG 概念插画：`manmandian-hero-16x9.png`、`manmandian-story-4-panels.png`、`manmandian-accessible-ways.png`、`manmandian-co-design.png`，均为 1672×941；✅
- SVG 信息图：`manmandian-three-steps.svg`、`manmandian-eight-guardrails.svg`、`manmandian-status-board.svg`、`manmandian-poems.svg`、`manmandian-mcp-35-map.svg`，均为 1600×900 viewBox；✅
- 全部图片为设计/说明素材，不是 live 截图、真实菜单或效果证据；来源见 `THIRD_PARTY_NOTICES.md`
- src/core（草稿/金额/快照/状态机）· src/adapters（真实 MCP + 隔离测试）· src/server · src/ui · src/accessibility · src/sign-language · tests/ · assets/{design,fixture,live}/ 其余内容：待建（P1 起）

## 主提示词存档

原文：`C:\Users\ASUS\Desktop\慢慢点_WorkBuddy完整执行提示词_单文件版.md`（v1.0，SHA-256 658b016c…c2fa6）。仓库内存档待完成：逐字节复制 + 哈希校验（P4 前）。
