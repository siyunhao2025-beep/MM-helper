# CODEBUDDY — 慢慢点恢复入口

## 目标

围绕麦当劳真实 MCP 的无障碍自主点餐 Skill：不催用户，不替用户决定。输入方式不同，决定权相同。

## 恢复顺序

1. 读 `.codebuddy/rules/manmandian.md`（短规则）
2. 读 `PROJECT_STATUS.md` → `CONTEXT_HANDOFF.md` → 相关 `DECISIONS.md`
3. 核对实际代码与 `docs/EVIDENCE_LEDGER.jsonl` 证据，不轻信文档自述
4. 完整需求：主提示词 v1.0（路径与 SHA-256 见 CONTEXT_HANDOFF.md）+ `requirements.lock.json`

## 真实架构（当前）

- 麦当劳官方 MCP（`https://mcp.mcd.cn`，工具清单以当前运行时定义与官方指南为准）经 WorkBuddy 连接器调用；2026-10-10 元数据快照含 35 项工具，脱敏契约位于 `.codebuddy/skills/manmandian/references/`
- 35 项分为八条生活任务路线：28 项读取/时间/核价按用户意图调用，7 项状态变更采用 `WRITE_MODE=GUIDE_ONLY`；历史 E1–E6 只证明 6 项有限范围真实执行
- 官方服务面向中国大陆地区（不含港澳台），Token 与个人会员账号绑定，仅限个人、非商业、正常频率的交互使用
- `auto-bind-coupons`、`cancel-order`、`create-order`、`delivery-create-address`、`draw-lottery`、`mall-create-order`、`party-order-create` 只生成解释、依赖与确认摘要，最终动作由用户在官方渠道完成；个人 Token 不用于企业代客、批量或无人值守调用
- 源代码 src/ 尚未建立（P1 任务）；运行 Skill 已重构，但 WorkBuddy 干净环境触发与完整任务仍待复测

## 有效工作流

- MCP 调用：经 WorkBuddy 连接器；仓库配置只保留 `${MCD_MCP_TOKEN}` 占位符，真实 Token 只进入本机受保护配置
- 推送前：依次核对 `git status --short`、`git diff --check`、逐文件 diff 与暂存区；只添加本次文件，不提交 Token、个人数据、代理或缓存配置
- 普通 main 分支：提交后安全同步 `origin/main` 再推送；Worktree 分支：`git push -u origin HEAD` 后创建 PR；禁止 force push
- 机器专用的凭证管理、代理与锁文件故障只在本机排查，不写进公共操作说明
- 本地开发与自动测试命令：待 src/ 建立后登记；现在没有，不编造

## 硬边界

真实交易/付费/外联/发布报名/个人数据共享需用户具体授权；企业或商业使用还需额外书面授权；金额整数分计算；没有真实证据不说完成。
