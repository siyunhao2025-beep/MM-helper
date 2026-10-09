# 官方来源清单（sources）

> 状态：S1–S3 已于 2026-10-09 真实核验（GitHub API 获取原文与 blob SHA）；S4–S10 未读，按需核验后更新本表。

| 编号 | 来源 | 核验状态 | 结论与版本 |
|---|---|---|---|
| S1 | M-China/mcd-developer-innovation-challenge · README.md | ✅ 已读 2026-10-09 | blob SHA 35fcb1e69b7dcb1ac6f4088195190a14db51aa34。必交文件：README / CONTEST_DECLARATION（内容不可改）/ MCP_INTEGRATION / 源代码 / workbuddy.md（WorkBuddy 专项必交）。报名窗口 2026-10-09 10:30 – 10-25 23:59 |
| S2 | 同上 · activityGuidelines.md | ✅ 已读 2026-10-09 | blob SHA e097cb899d2bbae5bf5f810d7196f3f9b960d29c。补充要求 mcp-config.example.json（仅环境变量占位）；仓库公开；创建时间窗口 2025-12-25 – 2026-10-25；参赛者须为中国大陆地区合法居民且≥18 岁；按 Star 排名 |
| S3 | 同上 · CONTEST_DECLARATION.md | ✅ 已读 2026-10-09 | blob SHA 136e76f3160317049f19f5ba03f4d0fedd70fc3c。原文已逐字入库本仓库根目录 |
| S4 | M-China/mcd-mcp-server（MCP 指南） | 未读 | 待读；服务范围与连接方式 |
| S5 | WorkBuddy 技能文档 open.workbuddy.cn/docs/skill | 未读 | 待读；SKILL.md 元数据格式 |
| S6 | WorkBuddy 连接器文档 | 未读 | 待读 |
| S7 | WorkBuddy 项目文档 | 未读 | 待读；.codebuddy/ 项目级配置 |
| S8 | WorkBuddy 记忆文档 | 未读 | 待读；记忆核验边界 |
| S9 | WCAG 2.2 w3.org/TR/WCAG22/ | 未读 | P1 无障碍设计前必读 |
| S10 | MediaPipe Gesture Recognizer | 未读 | 手语实验前必读（区分通用手势与中国手语） |

## 已发现的官方文件间差异（D005）

- README 必交文件表未列 `mcp-config.example.json`；activityGuidelines 列为必须 → 按更完整的 activityGuidelines 执行
- README 中 Issue 列表链接写作 M-China-Official 组织名，仓库实际在 M-China → 以实际仓库为准

## 需用户确认的资格事项（不阻塞开发，阻塞报名）

- activityGuidelines 要求参赛者为中国大陆地区合法居民、≥18 岁——需作者自行确认符合
