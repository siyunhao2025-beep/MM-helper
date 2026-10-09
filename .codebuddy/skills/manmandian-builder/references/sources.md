# 官方来源清单（sources）

> 最后核对：2026-10-09（北京时间）。官方内容可能更新；报名、发布或启用新能力前重新打开原始页面核验。文档支持不等于本轮账户或门店可用。

| 编号 | 一手来源 | 核验状态 | 当前结论 |
|---|---|---|---|
| S1 | [M-China/mcd-developer-innovation-challenge · README.md](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/README.md) | ✅ 已读；commit `bf5e651…`，blob `7ae70bc…` | README / CONTEST_DECLARATION（内容不可改）/ MCP_INTEGRATION / 源代码或可运行内容为参赛材料；参加 WorkBuddy 奖励需 workbuddy.md。报名截止 2026-10-25 23:59（北京时间） |
| S2 | [同仓库 · activityGuidelines.md](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/activityGuidelines.md) | ✅ 已读；blob `e097cb8…` | mcp-config.example.json 必须脱敏；仓库公开；创建时间窗口 2025-12-25 00:00—2026-10-25 23:59；按公开 Star 排名；未满 18 岁者取得父母或法定监护人同意后可参加 |
| S3 | [同仓库 · CONTEST_DECLARATION.md](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/CONTEST_DECLARATION.md) | ✅ 已读；blob `136e76f…` | 根目录官方声明与该 blob 一致，内容不可修改 |
| S4 | [M-China/mcd-mcp-server · README.md](https://github.com/M-China/mcd-mcp-server/blob/main/README.md) | ✅ 已读；commit `e90ecc5…`，blob `19ba45b…` | 服务面向中国大陆地区，不含港澳台；Streamable HTTP；官方地址 `https://mcp.mcd.cn`；指南标注 600 次/分钟上限；工具清单会更新，不固化总数 |
| S5 | [麦当劳 MCP 服务规则](https://cdn.mcd.cn/cms/pages/MCPServerRules.html) | ✅ 已读；页面版本日期 2025-12-03 | Token 与个人会员账号强绑定；授权为个人、不可转让、非独家、可撤销、非商业；禁止代下单/代领券牟利、批量高频与自动化调用；第三方 AI 输出以官方渠道为准 |
| S6 | [WorkBuddy / CodeBuddy 项目级 Skills](https://www.workbuddy.cn/docs/cli/skills) | ✅ 已读 | 项目级 Skill 位于 `.codebuddy/skills/<name>/SKILL.md`；核心 frontmatter 为 `name` 与 `description`，可选权限字段；描述负责触发 |
| S7 | [WorkBuddy 连接器](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Connector) | ✅ 已读 | 连接器支持手动配置 MCP；真实 Token 仅放本机配置，不进入仓库示例 |
| S8 | [WorkBuddy Git 集成与 Worktree](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Worktree-Task) | ✅ 已读 | 普通分支与 `workbuddy/*` Worktree 分支须区分；修改本地文件不等于已推送；Worktree 分支应推送后走 PR，不强推 |
| S9 | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | ✅ 已读；W3C Recommendation 2024-12-12 | 界面目标采用 AA：文字替代、键盘、焦点、对比度、重排、状态消息、24×24 CSS px 最小指针目标等；当前仓库尚未实现或实测，不得声称合规 |
| S10 | WorkBuddy 记忆文档 | 未专项核验 | 运行 Skill 不依赖永久记忆；会话草稿不得声称跨设备持久化 |
| S11 | MediaPipe Gesture Recognizer | 未读，暂不启用 | 手语能力当前关闭；推进 S1 前再核验，并区分通用手势与中国手语 |

## 官方材料间的差异与处理

- 比赛 README 的表格未列 `mcp-config.example.json`，activityGuidelines 将其列为最低文件之一：按更完整的 activityGuidelines 提供。
- 比赛 README 列“源代码”为必须，activityGuidelines 的最低文件列表未单列源代码：为降低审核风险，既保留可运行 Skill，也应补最小演示与测试，不能把治理文档当完整应用。
- 比赛 README 的 Issue 列表链接使用了 `M-China-Official`，实际活动仓库位于 `M-China`：报名以实际官方仓库与当时模板为准。
- 麦当劳 MCP 官方指南给出技术频率上限，但服务规则同时禁止批量、高频和自动化调用：项目按更严格的个人正常交互边界执行，不能把“低于 600 次/分钟”理解为允许自动化。

## 报名前需要作者本人确认

- 参赛者是中国大陆地区合法居民；如未满 18 周岁，已取得父母或法定监护人同意。
- `workbuddy.md` 是真实 WorkBuddy 上下文的完整、脱敏导出；当前摘要版可能不足以核验专项奖励。
- 开源许可证已经选择并与依赖、素材权利相容；Public 仓库本身不自动产生开源授权。
- 提交 Issue、公开发布和提供兑奖个人信息均由作者本人最终确认。
