# PROJECT_STATUS — 慢慢点

**更新**：2026-10-10（GMT+8）

**当前主工作包**：P0.8 35 工具契约、动态路由与能力图已完成；下一步仍为 P1 最小可运行核心

## 实际完成（均有文件或证据）

| 项 | 证据与边界 |
|---|---|
| 比赛 README / activityGuidelines / CONTEST_DECLARATION 刷新核验 | `.codebuddy/skills/manmandian-builder/references/sources.md`（当前 commit/blob） |
| 麦当劳 MCP 官方指南与服务规则核验 | sources.md S4/S5；确认中国大陆（不含港澳台）、个人非商业 Token、禁止批量高频自动化 |
| WorkBuddy 项目级 Skill / 连接器 / Git Worktree 文档核验 | sources.md S6–S8 |
| WCAG 2.2 一手标准核验 | sources.md S9；仅形成待测验收目标，不声称当前合规 |
| 真实只读链历史证据（账户/门店/菜单/详情/券/核价） | `docs/EVIDENCE_LEDGER.jsonl` E1–E6；范围有限，未在本次修订中重跑用户账号 |
| WorkBuddy 35 工具定义完整性校验 | `docs/EVIDENCE_LEDGER.jsonl` E18；35 个唯一名称、描述、输入 Schema 与哈希逐项对齐；本次采集调用 0 次，未与历史 live 证据混写 |
| 35 工具动态路由与脱敏契约 | `.codebuddy/skills/manmandian/references/`；八条生活任务路线、28 项读取/核价、7 项 `GUIDE_ONLY` 状态变更；当前运行时名称优先 |
| 面向用户的运行 Skill 重构 | `.codebuddy/skills/manmandian/SKILL.md`；从五工具快线扩展为全量识别、按意图分级调用和用户作主的肯定式规则；skill-creator 结构校验通过 |
| 可重复静态验收 | `.codebuddy/skills/manmandian/scripts/validate_contracts.py`；118/118 项通过，覆盖清单、哈希、路由、公开语言、链接、SVG、证据与官方声明（E19） |
| 视觉叙事版 README | `README.md`；新增 35 工具能力图，保留中英原创诗、真实状态、个人/企业价值、合规、安装、上传与报名核对 |
| 4 张 16:9 概念插画 | `assets/*.png`；均为 1672×941，使用汉堡、鸡肉汉堡、薯条、麦乐鸡与饮料语义，无官方 Logo、真实顾客或官方背书暗示 |
| 5 张精确中文 SVG 信息图 | 三步流程、八项护栏、状态看板、中英诗海报、35 工具地图；均为 1600×900 viewBox，并完成离线浏览器渲染检查 |
| 官方参赛声明原文保持不变 | `CONTEST_DECLARATION.md` 与官方 blob `136e76f…` 一致 |

## 阻塞、风险与未知

| 项 | 类型 | 处置 |
|---|---|---|
| 独立应用源代码、自动测试与演示 | 未完成 | P1 建立最小可运行核心，降低“只有文档/Skill”的复现和参赛审核风险 |
| WorkBuddy 运行 Skill 自动触发与完整任务 | 未复测 | 在干净 WorkBuddy 工作区做门店→菜单→详情→核价→沟通卡任务并留证 |
| 35 项工具 live 覆盖 | 29 项仍无真实执行回执 | 先按本人真实需求逐项、有限、合规验证；状态变更工具继续 `GUIDE_ONLY` |
| 运行时与官方公开表命名差异 | 已记录 | 每次会话优先当前运行时定义，持续核对官方更新 |
| `workbuddy.md` 完整原始上下文 | 待作者操作 | 当前为摘要版；参加专项奖励前须从真实 WorkBuddy 会话完整、脱敏导出 |
| 读屏、键盘、大字、窄屏 | 未实现/未测 | P1/P2 编码后使用 NVDA、VoiceOver、TalkBack 和真实任务测试 |
| 手语 S1 | BLOCKED | 无合法模型、限定词表和手语使用者共创；保持关闭，不打开相机 |
| 企业试点或商业部署 | 未授权 | 个人 MCP Token 不可用于企业；须另获麦当劳书面授权与隐私安全评审 |
| 参赛资格 | 需作者确认 | 中国大陆合法居民；未满 18 岁需父母或法定监护人同意 |
| LICENSE | 待作者决定 | Public 不自动等于开源；核对依赖与素材后选择许可 |

## 下一步（P1 主工作包）

建立 `src/core/` 共享草稿、整数分金额、报价快照失效逻辑、未下单沟通卡、35 工具路由器与最小可访问界面，并配套 fixture 测试。所有 live MCP 测试与 fixture 隔离；状态变更继续采用 `GUIDE_ONLY`。

## 授权边界

- 已获授权：将本轮 35 工具优化、肯定式运行 Skill、能力图及一致性修订提交并推送到 `siyunhao2025-beep/MM-helper` 的 `main`
- 未授权：真实下单/取消/付费、发布报名 Issue、企业部署、对外联系、收集或分享个人数据
