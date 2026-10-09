# CODEBUDDY — 慢慢点恢复入口

## 目标

围绕麦当劳真实 MCP 的无障碍自主点餐 Skill：不催用户，不替用户决定。输入方式不同，决定权相同。

## 恢复顺序

1. 读 `.codebuddy/rules/manmandian.md`（短规则）
2. 读 `PROJECT_STATUS.md` → `CONTEXT_HANDOFF.md` → 相关 `DECISIONS.md`
3. 核对实际代码与 `docs/EVIDENCE_LEDGER.jsonl` 证据，不轻信文档自述
4. 完整需求：主提示词 v1.0（路径与 SHA-256 见 CONTEXT_HANDOFF.md）+ `requirements.lock.json`

## 真实架构（当前）

- 麦当劳官方 MCP（mcp.cn，35 工具）经 WorkBuddy 连接器调用；真实只读链已验证（门店→菜单→详情→券→核价）
- 写操作（create-order/cancel-order）默认关闭，需独立授权+代码门禁
- 源代码 src/ 尚未建立（P1 任务）

## 有效命令（实际可运行）

- MCP 调用：经 WorkBuddy 连接器（配置见 mcp-config.example.json，Token 环境变量注入）
- 推送仓库（E10 实测通过，2026-10-09）：
  ```bash
  rm -f "C:/Users/ASUS/AppData/Local/Programs/WorkBuddy/resources/vendor/PortableGit/etc/gitconfig.lock"
  GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never GCM_GUI_PROMPT=false \
    git -c credential.helper=manager -c http.proxy=http://127.0.0.1:7897 push origin main
  ```
  （GitHub MCP 连接器只有读权限；helper-selector 在此环境会挂起，勿用默认配置推送）
- 本地开发与测试命令：待 src/ 建立后在此登记（现在没有，不编造）

## 硬边界

真实交易/付费/外联/发布报名/个人数据共享需用户具体授权；金额整数分计算；没有真实证据不说完成。
