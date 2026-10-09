# PROJECT_STATUS — 慢慢点

**更新**：2026-10-09 18:34（GMT+8）

**当前主工作包**：P0.5 公开交付与合规复核已完成；下一步仍为 P1 最小可运行核心

## 实际完成（均有文件或证据）

| 项 | 证据与边界 |
|---|---|
| 比赛 README / activityGuidelines / CONTEST_DECLARATION 刷新核验 | `.codebuddy/skills/manmandian-builder/references/sources.md`（当前 commit/blob） |
| 麦当劳 MCP 官方指南与服务规则核验 | sources.md S4/S5；确认中国大陆（不含港澳台）、个人非商业 Token、禁止批量高频自动化 |
| WorkBuddy 项目级 Skill / 连接器 / Git Worktree 文档核验 | sources.md S6–S8 |
| WCAG 2.2 一手标准核验 | sources.md S9；仅形成待测验收目标，不声称当前合规 |
| 真实只读链历史证据（账户/门店/菜单/详情/券/核价） | `docs/EVIDENCE_LEDGER.jsonl` E1–E6；范围有限，未在本次修订中重跑用户账号 |
| 面向用户的运行 Skill 重构 | `.codebuddy/skills/manmandian/SKILL.md`；结构校验通过，WorkBuddy 干净环境触发待复测 |
| 公开 README 总体重构 | `README.md`；含中英原创诗、真实状态、个人/企业价值、合规、安装、上传与报名核对 |
| 16:9 项目主视觉 | `assets/manmandian-hero-16x9.png`；1672×941，麦当劳餐品语义，无官方 Logo、真实顾客或官方背书暗示 |
| 官方参赛声明原文保持不变 | `CONTEST_DECLARATION.md` 与官方 blob `136e76f…` 一致 |

## 阻塞、风险与未知

| 项 | 类型 | 处置 |
|---|---|---|
| 独立应用源代码、自动测试与演示 | 未完成 | P1 建立最小可运行核心，降低“只有文档/Skill”的复现和参赛审核风险 |
| WorkBuddy 运行 Skill 自动触发与完整任务 | 未复测 | 在干净 WorkBuddy 工作区做门店→菜单→详情→核价→沟通卡任务并留证 |
| `workbuddy.md` 完整原始上下文 | 待作者操作 | 当前为摘要版；参加专项奖励前须从真实 WorkBuddy 会话完整、脱敏导出 |
| 读屏、键盘、大字、窄屏 | 未实现/未测 | P1/P2 编码后使用 NVDA、VoiceOver、TalkBack 和真实任务测试 |
| 手语 S1 | BLOCKED | 无合法模型、限定词表和手语使用者共创；保持关闭，不打开相机 |
| 企业试点或商业部署 | 未授权 | 个人 MCP Token 不可用于企业；须另获麦当劳书面授权与隐私安全评审 |
| 参赛资格 | 需作者确认 | 中国大陆合法居民；未满 18 岁需父母或法定监护人同意 |
| LICENSE | 待作者决定 | Public 不自动等于开源；核对依赖与素材后选择许可 |

## 下一步（P1 主工作包）

建立 `src/core/` 共享草稿、整数分金额、报价快照失效逻辑、未下单沟通卡与最小可访问界面，并配套 fixture 测试。所有 live MCP 测试与 fixture 隔离；写操作继续关闭。

## 授权边界

- 已获授权：将本轮 README、运行 Skill、主视觉及一致性修订提交并推送到 `siyunhao2025-beep/MM-helper` 的 `main`
- 未授权：真实下单/取消/付费、发布报名 Issue、企业部署、对外联系、收集或分享个人数据
