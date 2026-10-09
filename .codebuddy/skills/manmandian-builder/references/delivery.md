# 逐文件交付合同（delivery）

> 依据主提示词 v1.0 第 16、17 节。状态列如实更新；"待建"不算完成。

## 官方根材料（比赛必交）

| 路径 | 状态 | 验收要点 |
|---|---|---|
| README.md | ✅ 已建 | 首屏区分已实现/实验/未测；不写假截图假统计 |
| CONTEST_DECLARATION.md | ✅ 已建（官方原文） | 内容与官方 blob 136e76f… 一致，不可改动 |
| MCP_INTEGRATION.md | ✅ 已建 | 实际工具/调用链/证据索引；只读与写入边界 |
| mcp-config.example.json | ✅ 已建 | 仅 ${MCD_MCP_TOKEN} 占位，无真实凭证 |
| workbuddy.md | ⚠️ 摘要版 | 需作者导出完整 WorkBuddy 上下文替换 |
| 源代码 src/ | 待建（P1） | 可运行内容，形式不限 |
| LICENSE | 待作者确认 | 与依赖兼容后添加 |

## 项目规则与防偏离

| 路径 | 状态 |
|---|---|
| PROJECT_CONSTITUTION.md / requirements.lock.json / PROJECT_STATUS.md / DECISIONS.md / CONTEXT_HANDOFF.md | ✅ 已建 |
| .codebuddy/rules/manmandian.md | ✅ 已建（2026-10-09 观察到 CODEBUDDY.md 被客户端自动加载） |
| .codebuddy/CODEBUDDY.md | ✅ 已建（恢复入口） |
| 项目内主提示词存档 | 待办：逐字节复制 + SHA-256 校验后入库 |

## Skill 与源码（目标结构）

| 路径 | 状态 |
|---|---|
| .codebuddy/skills/manmandian-builder/（SKILL.md + references/×3） | ✅ 已建 |
| .codebuddy/skills/manmandian/SKILL.md（运行 Skill） | ✅ 已建 |
| src/core/ 草稿·金额·快照·状态机 | 待建（P1） |
| src/adapters/ 真实 MCP 适配器 + 测试适配器（隔离） | 待建 |
| src/server/、src/ui/、src/accessibility/、src/sign-language/ | 待建（按阶段） |
| tests/ | 待建；写入测试默认关闭 |

## docs 与素材（目标全集）

SOURCE_REGISTER（并入 builder references/sources.md）· MCP_CAPABILITY_MATRIX ✅ · FEATURE_STATUS 待建 · EVIDENCE_LEDGER.jsonl ✅ · FILE_MAP ✅ · ACCESSIBILITY 待建 · ACCESSIBILITY_TEST_REPORT 待建（未测写未测）· SIGN_LANGUAGE_MODEL_CARD 待建 · DATA_AND_CONSENT 待建 · TEST_REPORT 待建 · USER_VALUE_EVALUATION 待建 · DEMO_SCRIPT 待建 · SUBMISSION_CHECKLIST 待建 · KNOWN_LIMITATIONS ✅ · THIRD_PARTY_NOTICES ✅ · assets/{design,fixture,live}/ 待建（分目录分标签）

## 图文要求（第 17 节）

必含图组：首屏、候选、套餐核价/修改、双向文字、读屏键盘步骤、手语实验/拒识、MCP 链路、失败恢复。每图有 alt 与文字等价；设计/fixture/live 分标签；没有真实数据不画效益图；视频有字幕与文字稿。
