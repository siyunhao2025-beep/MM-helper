# 逐文件交付合同（delivery）

> 依据主提示词 v1.0 第 16、17 节。状态列如实更新；"待建"不算完成。

## 官方根材料（比赛必交）

| 路径 | 状态 | 验收要点 |
|---|---|---|
| README.md | ✅ 视觉叙事版（2026-10-10） | 9 个视觉入口；含项目定位、两首原创诗、35 工具地图、真实状态、个人/企业边界、安装、示例、合规、上传和报名核对；不写假统计 |
| CONTEST_DECLARATION.md | ✅ 已建（官方原文） | 内容与官方 blob 136e76f… 一致，不可改动 |
| MCP_INTEGRATION.md | ✅ 已建 | 35 项实际工具、八条路线、证据分层、28 项读取/核价与 7 项状态变更门控 |
| mcp-config.example.json | ✅ 已建 | 仅 ${MCD_MCP_TOKEN} 占位，无真实凭证 |
| workbuddy.md | ⚠️ 摘要版 | 需作者导出完整 WorkBuddy 上下文替换 |
| 可运行内容 / 源代码 | ⚠️ 运行 Skill 已建，独立 src/ 待建（P1） | 官方 README 要求源代码或可运行内容；提交前补最小演示与测试可降低审核风险 |
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
| .codebuddy/skills/manmandian/SKILL.md（运行 Skill） | ✅ 已扩展为 35 项动态发现与分级路由；肯定式语言、UTF-8 结构和 118 项静态检查通过；WorkBuddy 干净环境触发待复测 |
| .codebuddy/skills/manmandian/references/ | ✅ `mcd-tool-router.md` + `mcd-tool-contracts.json`；35 个唯一工具与输入契约，原始供应方示例留在本机 |
| .codebuddy/skills/manmandian/scripts/validate_contracts.py | ✅ 标准库自检；覆盖 35 项清单、28/7 分层、脱敏哈希、公开语言、SVG、链接、证据与官方声明 |
| src/core/ 草稿·金额·快照·状态机 | 待建（P1） |
| src/adapters/ 真实 MCP 适配器 + 测试适配器（隔离） | 待建 |
| src/server/、src/ui/、src/accessibility/、src/sign-language/ | 待建（按阶段） |
| tests/ | 待建；写入测试默认关闭 |

## docs 与素材（目标全集）

SOURCE_REGISTER（并入 builder references/sources.md）✅ · MCP_CAPABILITY_MATRIX ✅ · FEATURE_STATUS 待建 · EVIDENCE_LEDGER.jsonl ✅ · FILE_MAP ✅ · ACCESSIBILITY 待建 · ACCESSIBILITY_TEST_REPORT 待建（未测写未测）· SIGN_LANGUAGE_MODEL_CARD 待建 · DATA_AND_CONSENT 待建 · TEST_REPORT 待建 · USER_VALUE_EVALUATION 待建 · DEMO_SCRIPT 待建 · SUBMISSION_CHECKLIST 待建 · KNOWN_LIMITATIONS ✅ · THIRD_PARTY_NOTICES ✅ · 4 张 PNG 概念插画 + 5 张 SVG 信息图 ✅（均非 live 截图）· assets/{design,fixture,live}/ 其余待建

## 图文要求（第 17 节）

必含图组：首屏、候选、套餐核价/修改、双向文字、读屏键盘步骤、手语实验/拒识、MCP 链路、失败恢复。每图有 alt 与文字等价；设计/fixture/live 分标签；没有真实数据不画效益图；视频有字幕与文字稿。
