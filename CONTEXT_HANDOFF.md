# CONTEXT_HANDOFF

项目：慢慢点（ManManDian）

主仓库：<https://github.com/siyunhao2025-beep/MM-helper>（main）

主提示词：`慢慢点_WorkBuddy完整执行提示词_单文件版.md` v1.0；历史记录 SHA-256 `658b016c3be2c3ab1579586931e255ce011b6213fe34a00dd1d297acfd2c2fa6`；仓库内逐字节存档仍待完成

## 当前结论

- README 与运行 Skill 已完成整体重构；README 为视觉叙事版，包含 4 张 16:9 概念插画与 5 张精确中文 SVG 信息图，长技术说明使用可展开区保留。
- 2026-10-10 WorkBuddy 导出的 35 项 mcd-mcp 定义已完成独立校验：名称、描述、输入 Schema 与 Schema 哈希均 35/35 对齐；采集会话调用数为 0，原始导出留在作者本机，仓库保存脱敏契约和来源哈希。
- 运行 Skill 已从五工具固定白名单升级为动态发现：35 项分为八条生活任务路线；28 项读取、时间与核价工具按用户意图调用；7 项状态变更工具采用 `WRITE_MODE=GUIDE_ONLY`。
- README、运行 `SKILL.md`、MCP 集成、路由手册与 5 张文字型 SVG 可见文字已通过肯定式表达扫描；目标汉字与常见英文否定形式计数均为 0。运行 Skill 通过分级路由、数据最小范围和“用户作主”保持安全边界。
- 全部菜单视觉统一为汉堡、鸡肉汉堡、薯条、麦乐鸡与饮料，不使用官方 Logo、官方包装、真实顾客或背书暗示；每张图都有替代文字，关键信息图另有纯文字版。
- 麦当劳 MCP 官方服务范围已核验为中国大陆地区，不含港澳台；旧“澳门未知”结论已删除。
- Token 与个人会员账号绑定，只能本人、非商业、正常交互使用；不得企业代客、商业运营、批量、高频或无人值守调用。
- 旧“参赛者必须年满 18 岁”结论已更正：未满 18 岁但取得父母或法定监护人同意者可参加。
- `.codebuddy/skills/manmandian/SKILL.md` 的 35 工具版已通过 skill-creator 结构校验与自带 118 项静态检查；干净 WorkBuddy 环境的自动触发与端到端任务仍待复测。
- 真实 MCP 只读链证据仍是 2026-10-09 的有限范围历史记录 E1–E6；本轮没有使用用户 Token 重跑。

## 未完成

- `src/`、独立界面、自动测试均未建立。
- 35 项中只有 6 项存在有限范围历史 live 证据，其余 29 项继续保持元数据已取得、真实执行待验证。
- 读屏、键盘、大字、窄屏均未实测。
- `workbuddy.md` 仍为摘要版，专项奖励材料存在核验风险。
- 手语 S1 无合法模型、词表与真实共创，保持 BLOCKED。
- LICENSE 未选择；主提示词原文未入库。
- 企业或商业部署未获授权。

## 下一条动作

进入 P1：实现共享草稿、整数分金额、报价快照失效、未下单沟通卡、35 工具路由器和最小可访问界面，先用 fixture 跑通自动测试，再在获得具体授权时做有限 live 只读复测。

## 恢复顺序

1. 读 `PROJECT_CONSTITUTION.md` 与 `PROJECT_STATUS.md`
2. 读本文件与 `DECISIONS.md` 的最新决定
3. 读 `.codebuddy/skills/manmandian-builder/references/sources.md`
4. 读 `.codebuddy/skills/manmandian/references/mcd-tool-router.md` 与对应契约条目
5. 核对实际文件、Git 状态与 `docs/EVIDENCE_LEDGER.jsonl`；文档自述不能替代代码和测试

授权边界：本轮仅授权仓库内容优化与推送；未授权真实交易、报名发布、企业部署或外联。
