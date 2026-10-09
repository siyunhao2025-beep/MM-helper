# DECISIONS

## D001 · 2026-10-09 · v1.0 单文件版取代 v0.2/v0.3
- **依据**：用户提供《慢慢点_WorkBuddy完整执行提示词_单文件版.md》（v1.0，SHA-256 658b016c3be2c3ab1579586931e255ce011b6213fe34a00dd1d297acfd2c2fa6），文首声明取代旧版指令。
- **影响**：旧 v0.3 时期产生的本地工作区治理文件保留不删；仓库以 v1.0 为准建档。
- **来源**：USER_PROVIDED。

## D002 · 2026-10-09 · 项目主仓库定为 MM-helper
- **依据**：用户明确指令「使用我已登录的账号访问 github.com/siyunhao2025-beep/MM-helper 并在该仓库下添加内容」。
- **核验**：仓库为空（无分支无提交）、public、创建于 2026-10-09T09:17Z（在参赛资格窗口内）、已确认 push 权限。
- **影响**：无既有代码需要匹配风格；从零按主提示词第 16 节文件地图建立结构。
- **来源**：USER_PROVIDED。

## D003 · 2026-10-09 · .codebuddy 目录命名与加载策略
- **依据**：主提示词第 13.2/15.2 节按 WorkBuddy 官方项目文档使用 .codebuddy/ 目录。
- **决定**：规则文件写入 .codebuddy/rules/，恢复入口写 .codebuddy/CODEBUDDY.md；**自动加载未验证**，在验证前每轮开发采用显式读取，不声称已配置永久记忆。
- **来源**：DESIGN_PROPOSAL（依官方文档格式）。

## D004 · 2026-10-09 · LICENSE 暂不添加
- **依据**：主提示词第 16.1 节要求许可需作者确认且与依赖兼容。
- **影响**：LICENSE 文件待作者确认后添加；已在 docs/KNOWN_LIMITATIONS.md 登记。
- **来源**：DESIGN_PROPOSAL。

## D005 · 2026-10-09 · 官方规则差异处理
- **事实**：官方 README 必交文件表未列 mcp-config.example.json，而 activityGuidelines 列为必须。
- **决定**：按更完整的 activityGuidelines 执行（提供该文件）。
- **来源**：DOC_CONFIRMED（两文件 SHA 见 docs/SOURCE_REGISTER.md）。
