# 逐文件交付合同（delivery）

> 依据主提示词 v1.0 第 16、17 节。状态列如实更新；"待建"不算完成。

## 官方根材料（比赛必交）

| 路径 | 状态 | 验收要点 |
|---|---|---|
| README.md | ✅ 视觉叙事版（2026-10-13） | 9 个图片入口 + 1 个 Mermaid 决策流程；含项目定位、两首原创诗、35 工具地图、可运行护栏、真实状态、个人/企业边界、安装、示例、合规、上传和报名核对；不写假统计 |
| CONTEST_DECLARATION.md | ✅ 已建（官方原文） | 内容与官方 blob 136e76f… 一致，不可改动 |
| MCP_INTEGRATION.md | ✅ 已建 | 35 项实际工具、八条路线、证据分层、28 项读取/核价与 7 项状态变更门控 |
| mcp-config.example.json | ✅ 已建 | 仅 ${MCD_MCP_TOKEN} 占位，无真实凭证 |
| workbuddy.md | ⚠️ 结构化公开索引已建 | 专项奖励前由作者放入 WorkBuddy 原生对话导出，并按索引完成脱敏对账 |
| 可运行内容 / 源代码 | ✅ 运行 Skill、决定权护栏、CLI、fixture 与 66 项业务测试已建 | 官方 README 接受源代码或可运行内容；独立可访问界面与 WorkBuddy 端到端复测继续提升复现体验和产品成熟度 |
| LICENSE | ✅ 标准 MIT | 作者确认版权行公开署名；第三方权利另见 THIRD_PARTY_NOTICES.md |

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
| .codebuddy/skills/manmandian/SKILL.md（运行 Skill） | ✅ 已扩展为 35 项动态发现、分级路由、三态候选、证据模式、无障碍回应与本地护栏；肯定式语言与 UTF-8 结构检查通过；WorkBuddy 干净环境触发待复测 |
| .codebuddy/skills/manmandian/references/ | ✅ 工具路由 + 机器契约 + 决定权契约 + 无障碍回应模式；35 个唯一工具与输入契约，原始供应方示例留在本机 |
| .codebuddy/skills/manmandian/scripts/validate_contracts.py | ✅ 标准库自检；覆盖 35 项清单、28/7 分层、脱敏哈希、公开语言、SVG、链接、证据、许可证、决定权护栏、跨文档一致性与官方声明 |
| src/core/ 草稿·金额·快照·候选·沟通卡 | ✅ P1.1 零依赖实现；fixture/live 证据模式隔离，7 项状态变更保持 `GUIDE_ONLY` |
| src/adapters/ 真实 MCP 适配器 + 测试适配器（隔离） | 待建 |
| src/server/、src/ui/、src/accessibility/、src/sign-language/ | 待建（按阶段） |
| examples/ + tests/ | ✅ 脱敏 fixture + 66 项本地自动测试；真实 MCP 与辅助技术测试仍待完成 |

## docs 与素材（目标全集）

SOURCE_REGISTER（并入 builder references/sources.md）✅ · MCP_CAPABILITY_MATRIX ✅ · FEATURE_STATUS 待建 · EVIDENCE_LEDGER.jsonl ✅ · FILE_MAP ✅ · ACCESSIBILITY 待建 · ACCESSIBILITY_TEST_REPORT 待建（未测写未测）· SIGN_LANGUAGE_MODEL_CARD 待建 · DATA_AND_CONSENT 待建 · TEST_REPORT 待建 · USER_VALUE_EVALUATION 待建 · DEMO_SCRIPT 待建 · SUBMISSION_CHECKLIST 待建 · KNOWN_LIMITATIONS ✅ · THIRD_PARTY_NOTICES ✅ · 4 张 PNG 概念插画 + 5 张 SVG 信息图 ✅（均非 live 截图）· assets/{design,fixture,live}/ 其余待建

## 图文要求（第 17 节）

必含图组：首屏、候选、套餐核价/修改、双向文字、读屏键盘步骤、手语实验/拒识、MCP 链路、失败恢复。每图有 alt 与文字等价；设计/fixture/live 分标签；没有真实数据不画效益图；视频有字幕与文字稿。
