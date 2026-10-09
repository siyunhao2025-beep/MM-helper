# PROJECT_STATUS — 慢慢点

**更新**：2026-10-09 17:45（GMT+8）
**当前主工作包**：P0 核验与建档（本仓库）→ 已完成，进入 P1

## 实际完成（均有证据）

| 项 | 证据 |
|---|---|
| 官方三文件核验（README/activityGuidelines/CONTEST_DECLARATION） | docs/SOURCE_REGISTER.md（含 SHA） |
| 官方声明原文入库（内容未改动） | CONTEST_DECLARATION.md |
| 真实只读链五环（账户/门店/菜单/详情/券/核价） | docs/EVIDENCE_LEDGER.jsonl E1–E6（traceId） |
| 治理建档（宪法/需求锁定/状态/决定/交接/规则） | 仓库根 + .codebuddy/ |
| builder 与运行 Skill 骨架 | .codebuddy/skills/ |

## 阻塞与未知

| 项 | 类型 | 处置 |
|---|---|---|
| S4 mcd-mcp-server 官方指南、S5–S10 文档 | 未读 | P1 期间补读并登记 |
| 参赛资格（规则要求中国大陆地区合法居民） | 需用户确认 | 不阻塞本地开发；报名前必须确认 |
| 主提示词仓库内存档 | 待办 | 逐字节复制+SHA-256 校验后入库（P4 前） |
| workbuddy.md 完整导出 | 待办 | 需作者在 WorkBuddy 客户端导出 |
| 澳门是否在 mcd.cn 服务区 | 未知 | 待真实调用验证 |

## 下一步（P1 主工作包）

src/core 共享草稿与金额整数分核心 + 可访问界面（文字/大字/读屏同源）+ 未下单沟通卡 + 报价快照（变更即失效）。

## 授权边界

- 本轮已获授权：向本仓库（siyunhao2025-beep/MM-helper）推送开发内容
- 未授权：真实下单/取消/付费、发布报名 Issue、外联、公开部署
