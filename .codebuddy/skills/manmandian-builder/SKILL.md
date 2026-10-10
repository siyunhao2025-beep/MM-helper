---
name: manmandian-builder
description: 「慢慢点」项目开发技能——基于麦当劳中国 MCP 的无障碍自主点餐助手开发规范、证据核验与反幻觉工作流。用户要求开发、审查、测试、交付或恢复慢慢点（ManManDian）、无障碍点餐、预算护栏、沟通卡、MCP 集成、参赛材料时使用；不用于替顾客实际选餐。开发中必须遵守中国大陆服务范围、个人非商业 Token 边界、只读默认、可访问性实测和比赛文件要求。
---

# 慢慢点 Builder Skill（开发技能）

> 依据《慢慢点 WorkBuddy 完整执行提示词（单文件整合版 v1.0）》第 15.1 节生成。本 Skill 指导 WorkBuddy **开发**本项目；顾客点餐请使用运行 Skill `manmandian`。

## 执行前置（每次启动/恢复必做）

1. 读 `.codebuddy/rules/manmandian.md`（短规则）
2. 读 `PROJECT_CONSTITUTION.md` → `PROJECT_STATUS.md` → `CONTEXT_HANDOFF.md` → 相关 `DECISIONS.md`
3. 核对实际代码与 `docs/EVIDENCE_LEDGER.jsonl`，不轻信文档自述
4. 需求索引：`requirements.lock.json`（R01–R22）

## 硬约束（违者即为造假）

- 事实七类标签：USER_PROVIDED / DOC_CONFIRMED / TOOL_OBSERVED / TEST_OBSERVED / DESIGN_PROPOSAL / ASSUMPTION / UNKNOWN
- 没有真实证据不说完成；不猜接口参数（schema 必须来自真实 tools/list 或真实返回）
- 不删失败测试、不放宽预算/安全/无障碍要求、不补写假日志
- 金额用整数分计算，展示时除以 100；确认绑定全要素，变更即失效
- 七项状态变更工具当前统一采用 `WRITE_MODE=GUIDE_ONLY`；未来开放调用还需用户对具体动作明确授权并通过代码门禁
- 麦当劳 MCP 仅面向中国大陆地区（不含港澳台）；个人 Token 不得用于企业代客、商业运营、批量、高频或无人值守调用
- 企业价值只可作为设计与待验证指标陈述；企业试点或部署必须另获麦当劳书面授权
- 同一问题连续 3 轮修复失败 → 记录最小复现与根因假设，停止盲改

## 阶段路线（P0–P5）

| 阶段 | 内容 | 退出条件 |
|---|---|---|
| P0 | 核验与建档 | 真实现状记录，不编历史 |
| P1 | 最小真实只读链 + 共享草稿/文字键盘核心 | 真实只读证据（已有）+ 可访问核心 |
| P2 | 可访问与交易保护 | 相关测试通过才申请交易验证 |
| P3 | 手语实验（条件推进） | 真实推理证据决定开放 |
| P4 | 验证与图文 | 每项功能有准确状态与证据 |
| P5 | 作者审核与提交 | 作者明确批准后执行 |

## 参考文件（真实存在）

- `references/truth-and-scope.md` — 真相与边界（事实分层、范围锁定、红线）
- `references/sources.md` — 官方来源清单与核验状态
- `references/delivery.md` — 逐文件交付合同与图文要求
- `../manmandian/references/mcd-tool-router.md` — 35 项运行时工具的人类可读路由
- `../manmandian/references/mcd-tool-contracts.json` — 35 项脱敏输入契约与快照校验信息

## 每轮汇报格式

只写：实际完成 / 真实验证 / 具体未知 / 下一项动作。给可核对路径（文件 + traceId + 测试命令）。
