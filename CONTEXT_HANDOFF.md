# CONTEXT_HANDOFF

项目：慢慢点（ManManDian）

主仓库：<https://github.com/siyunhao2025-beep/MM-helper>（main）

主提示词：`慢慢点_WorkBuddy完整执行提示词_单文件版.md` v1.0；历史记录 SHA-256 `658b016c3be2c3ab1579586931e255ce011b6213fe34a00dd1d297acfd2c2fa6`；仓库内逐字节存档仍待完成

## 当前结论

- README 与运行 Skill 已于 2026-10-09 完成整体重构；README 后续升级为视觉叙事版，包含 4 张 16:9 概念插画与 4 张精确中文 SVG 信息图，长技术说明折叠但没有删除。
- 全部菜单视觉统一为汉堡、鸡肉汉堡、薯条、麦乐鸡与饮料，不使用官方 Logo、官方包装、真实顾客或背书暗示；每张图都有替代文字，关键信息图另有纯文字版。
- 麦当劳 MCP 官方服务范围已核验为中国大陆地区，不含港澳台；旧“澳门未知”结论已删除。
- Token 与个人会员账号绑定，只能本人、非商业、正常交互使用；不得企业代客、商业运营、批量、高频或无人值守调用。
- 旧“参赛者必须年满 18 岁”结论已更正：未满 18 岁但取得父母或法定监护人同意者可参加。
- `.codebuddy/skills/manmandian/SKILL.md` 已通过结构校验，但尚未在干净 WorkBuddy 环境完成自动触发与端到端复测。
- 真实 MCP 只读链证据仍是 2026-10-09 的有限范围历史记录 E1–E6；本轮没有使用用户 Token 重跑。

## 未完成

- `src/`、独立界面、自动测试均未建立。
- 读屏、键盘、大字、窄屏均未实测。
- `workbuddy.md` 仍为摘要版，专项奖励材料存在核验风险。
- 手语 S1 无合法模型、词表与真实共创，保持 BLOCKED。
- LICENSE 未选择；主提示词原文未入库。
- 企业或商业部署未获授权。

## 下一条动作

进入 P1：实现共享草稿、整数分金额、报价快照失效、未下单沟通卡和最小可访问界面，先用 fixture 跑通自动测试，再在获得具体授权时做有限 live 只读复测。

## 恢复顺序

1. 读 `PROJECT_CONSTITUTION.md` 与 `PROJECT_STATUS.md`
2. 读本文件与 `DECISIONS.md` 的最新决定
3. 读 `.codebuddy/skills/manmandian-builder/references/sources.md`
4. 核对实际文件、Git 状态与 `docs/EVIDENCE_LEDGER.jsonl`；文档自述不能替代代码和测试

授权边界：本轮仅授权仓库内容优化与推送；未授权真实交易、报名发布、企业部署或外联。
