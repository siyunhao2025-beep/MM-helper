# WorkBuddy 开发上下文（公开核验索引）

> **官方定位**：活动仓库把 `workbuddy.md` 定义为“使用 WorkBuddy 开发时的对话上下文”，用于核验联动活动奖励条件。
>
> **当前形态**：本文件是依据真实 WorkBuddy 会话整理的结构化公开索引，便于审核者沿时间、工具、traceId 与产物哈希逐项核对。申请 WorkBuddy 专项奖励前，作者再从 WorkBuddy 导出原生对话上下文放入本文件，并用本索引完成脱敏与对账。文件格式与资格结论以活动组织者审核为准。
>
> **公开范围**：本索引仅收录时间、工具名、最小调用参数、脱敏结果摘要与核验标识；Token、密钥、手机号、收货地址、支付信息和他人个人信息由作者在本机受保护环境管理。

## 1. 开发环境

| 项 | 值 |
|---|---|
| 工具 | WorkBuddy 桌面版（本次比赛的官方合作工具） |
| 时间跨度 | 2026-10-09 起，最新记录 2026-10-10 |
| MCP 连接器 | `mcd-mcp`（WorkBuddy 自定义连接器，已启用） |
| MCP Server | 麦当劳中国官方 MCP，`https://mcp.mcd.cn`，Streamable HTTP |
| 认证 | Bearer Token；凭证保存在本机受保护配置 |
| 服务范围 | 中国大陆地区；港澳台由官方其他渠道承接 |
| 账户边界 | Token 与个人会员账号绑定，服务本人、个人用途与正常频率交互 |

## 2. 真实 MCP 调用记录（6 项）

来源：`docs/EVIDENCE_LEDGER.jsonl` E1–E6。六项均为读取或核价调用，状态变更调用为 0。traceId 作为官方核验线索保留；公开结果采用最小披露。

| 时间（GMT+8） | 工具 | 调用参数 | 公开结果摘要 | traceId |
|---|---|---|---|---|
| 10-09 15:34:29 | `query-my-account` | 无参 | 调用成功并返回积分字段；精确账户数值留在作者本机原始记录 | `f2a5c0be25b8b87ee1289978062e426d` |
| 10-09 17:05:31 | `query-nearby-stores` | `searchType=2, city=珠海, keyword=拱北口岸, beType=1` | 返回 5 家门店、营业信息与 `reservationTimeOptions`；到店自取链按返回字段继续 | `499b328d14a2486d5cfe23fe238fbf02` |
| 10-09 17:05:40 | `query-meals` | `storeCode=1440032, orderType=1, beType=1` | 返回 13 个分类与约 90 个当时在售商品；`data.meals` 为 code→详情映射 | `6127fb295975dece95a234be07bf1fa1` |
| 10-09 17:05:53 | `query-meal-detail` | `storeCode=1440032, orderType=1, beType=1, code=9900005456` | 返回 3 个 round、默认组合、特调键与差价字段 `diffPrice` | `a113b4cc956ba05cebd2e2e6de22d590` |
| 10-09 17:05:53 | `query-store-coupons` | `storeCode=1440032, orderType=1, beType=1` | `data=[]`，表示该账户、门店与时点的可用券数量为 0 | `aaeadd918889cad31e37c4294cc97335` |
| 10-09 17:06:09 | `calculate-price` | `storeCode=1440032, orderType=1, beType=1, items=[{productCode=9900005456, quantity=1}]` | 返回 `price=3800` 分、`discount=0` 与堂食/外带方式 | `d6e351dd8023714f13fdbafdced0b994` |

**证据边界**：六项记录证明对应时点和参数范围内的成功调用。其余 29 项保持“元数据已取得”状态，真实执行只随本人真实需求和工具授权推进。

## 3. WorkBuddy 工具定义采集（2026-10-10 11:14）

WorkBuddy 会话对 `mcd-mcp` 完成一次纯元数据采集，产出 raw JSON、catalog JSONL、matrix Markdown、capture report 与 SHA-256 清单。

| 校验项 | 结果 |
|---|---:|
| 工具记录总数 | 35 |
| 唯一运行时名称 | 35 / 35 |
| raw 与 catalog 名称一致 | 35 / 35 |
| raw 与 catalog 描述一致 | 35 / 35 |
| raw 与 catalog `inputSchema` 一致 | 35 / 35 |
| source schema SHA-256 可复算 | 35 / 35 |
| 本次业务工具调用次数 | 0 |
| 本次状态变更次数 | 0 |
| Token 与真实个人数据模式扫描 | 0 命中 |

采集来源：`WORKBUDDY_INJECTED_METADATA`。WorkBuddy 把工具定义注入会话；本轮原始 `tools/list` 响应仍待取得。运行时为 35 项提供名称、描述与 `inputSchema`，`outputSchema` 与 `annotations` 字段均为 null。以上边界已写入采集报告与脱敏契约。

产物哈希：

- `01-mcd-tools-raw.json`：`a97406cb3438268b28aef9e1c64e6e6113fc47c2b6752b9b9991da3ab5219413`
- `02-mcd-tools-catalog.jsonl`：`92fea9c0e31248c628531784364cad15cab541133e44df8e0ac5d1107ce36d57`
- `03-mcd-tools-matrix.md`：`4617b70bffd537823c836d7f90e81cdefef93136fe629fd25bfefc8262c0e6c9`
- `04-mcd-tools-capture-report.md`：`9a3eb7e171c316c0426d7c5103902c692a93f29a09e15c8e90b7a102ca12ce0b`

## 4. 2026-10-10 会话活动索引

本节依据 WorkBuddy 会话整理记录，原生对话导出用于最终逐项复核。

| 时间（GMT+8） | 会话活动 | 可核验结果 |
|---|---|---|
| 13:09 | 从 GitHub 拉取 `siyunhao2025-beep/MM-helper`，审阅两个 Skill 后安装到 WorkBuddy 用户级技能目录 | 运行脚本为标准库静态校验器；审阅记录显示网络、子进程与写文件调用数量为 0 |
| 13:14 | 在完整仓库根目录运行当时版本的仓库自检 | 当时输出 `PASS: 118 checks` |
| 13:25 | 复核比赛规则文件 | README / activityGuidelines / CONTEST_DECLARATION / RANKING 四份材料已读取 |
| 13:27 | 比对 `CONTEST_DECLARATION.md` 与官方原文 | git blob SHA-1 同为 `136e76f3160317049f19f5ba03f4d0fedd70fc3c` |
| 13:30 | 核实报名 Issue 仓库 | 官方活动仓库为 `M-China/mcd-developer-innovation-challenge` |

## 5. WorkBuddy 本轮已推送变更

- 新增标准 MIT `LICENSE`
- 本文件从摘要占位升级为结构化公开索引
- `README.md` 中三处许可证状态同步更新
- `THIRD_PARTY_NOTICES.md` 增加许可证、第三方材料与商标边界

对应提交：`3cd384b`、`48451eb`。后续复核继续修正跨文档状态、公开隐私最小化和校验覆盖。

## 6. 需求来源

主提示词《慢慢点 WorkBuddy 完整执行提示词（单文件整合版 v1.0）》由项目作者提供，历史 SHA-256 为 `658b016c…c2fa6`。

## 7. 运行与提交边界

- 35 项工具的元数据快照与 6 项历史真实调用分层陈述。
- 7 项状态变更工具（`create-order`、`cancel-order`、`auto-bind-coupons`、`delivery-create-address`、`draw-lottery`、`mall-create-order`、`party-order-create`）统一采用 `WRITE_MODE=GUIDE_ONLY`。
- 最终交易、权益与地址动作由用户在麦当劳官方渠道逐次决定。
- 专项奖励提交前，由作者放入 WorkBuddy 原生对话上下文并完成个人信息脱敏；本索引保留为对账地图。
