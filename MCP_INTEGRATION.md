# MCP_INTEGRATION — 麦当劳 MCP 真实集成说明

> 本文件把“官方文档写了什么”“WorkBuddy 本轮看见什么”“项目曾经真实跑过什么”分开记录。完整字段契约见 `.codebuddy/skills/manmandian/references/mcd-tool-contracts.json`，逐工具状态见 `docs/MCP_CAPABILITY_MATRIX.md`，真实调用证据见 `docs/EVIDENCE_LEDGER.jsonl`。

## 1. 服务器、账户与使用范围

- Server：麦当劳中国官方 MCP，Streamable HTTP，官方地址 `https://mcp.mcd.cn`
- 认证：Bearer Token；本人在 `open.mcd.cn/mcp` 申请，仓库只保存 `${MCD_MCP_TOKEN}` 占位示例
- 服务范围：中国大陆地区，港澳台位于当前服务范围外
- 账户边界：Token 与个人会员账号绑定，服务本人、个人用途与正常频率交互
- 企业价值：当前用于流程共创、无障碍设计与匿名评估；企业试点、门店系统集成与商业部署以麦当劳书面授权为启动条件

## 2. 2026-10-10 工具定义快照

WorkBuddy 导出了五个文件：原始 JSON、逐行目录、Markdown 矩阵、采集报告和 SHA-256 清单。项目完成了独立交叉校验：

| 检查项 | 结果 |
|---|---:|
| 原始工具数 | 35 |
| 逐行目录记录数 | 35 |
| 唯一运行时名称 | 35 |
| 名称逐项对齐 | 35 / 35 |
| 描述逐项对齐 | 35 / 35 |
| 输入 Schema 逐项对齐 | 35 / 35 |
| Schema SHA-256 可复算 | 35 / 35 |
| 本次业务调用 | 0 |
| 本次状态变更调用 | 0 |
| `outputSchema` 已提供 | 0 / 35 |
| MCP `annotations` 已提供 | 0 / 35 |

采集来源字段为 `WORKBUDDY_INJECTED_METADATA`。这表示 WorkBuddy 向会话注入了工具定义；本轮没有取得原始 `tools/list` 响应，也没有取得 WorkBuddy 版本与 Server URL 字段，因此这两项继续保留为 `UNKNOWN`。官方公开指南单独确认 Server URL。

原始导出保留在作者本机。仓库只收录脱敏派生契约，供应方说明中的姓名、手机号、地址和订单号示例已排除。四个来源文件哈希：

- raw JSON：`a97406cb3438268b28aef9e1c64e6e6113fc47c2b6752b9b9991da3ab5219413`
- catalog JSONL：`92fea9c0e31248c628531784364cad15cab541133e44df8e0ac5d1107ce36d57`
- matrix Markdown：`4617b70bffd537823c836d7f90e81cdefef93136fe629fd25bfefc8262c0e6c9`
- capture report：`9a3eb7e171c316c0426d7c5103902c692a93f29a09e15c8e90b7a102ca12ce0b`

## 3. 运行时名称优先

当前 WorkBuddy 快照的全名格式为：

~~~text
mcp__mcd-mcp__<short-name>
~~~

界面可显示短名。Skill 每次会话先读取当前真实工具定义，再建立短名到全名的映射。优先级为：

~~~text
当前运行时定义
→ 当前真实返回
→ 当前官方指南与服务规则
→ 2026-10-10 脱敏快照
→ 2026-10-09 历史证据
→ 模型常识
~~~

2026-10-10 核对发现两类差异：

1. 运行时名称为 `query-party-store-date`、`query-party-store-session`；当日官方公开表写作 `query-partystore-date`、`query-partystore-session`。
2. 运行时还提供 `query-promotions` 与 `query-survey-coupon`；当日官方公开工具表尚未列入这两项。

真实调用采用当前运行时名称。35 是时点快照，下一次运行继续动态发现。

## 4. 两层证据状态

### 4.1 定义已取得

35 个工具全部达到 `METADATA_CAPTURED`：名称、说明与输入 Schema 已取得。本次采集状态统一为 `NOT_TESTED`，因为采集会话的业务调用数为 0。

### 4.2 有限范围真实执行

2026-10-09 的 E1–E6 为独立历史证据，共 6 项：

| 工具 | 真实执行 | 范围 |
|---|---|---|
| `query-my-account` | 成功 | 当前单一账户的积分字段 |
| `query-nearby-stores` | 成功 | 珠海拱北、到店自取、5 家门店 |
| `query-meals` | 成功 | 门店 1440032 的当时菜单 |
| `query-meal-detail` | 成功 | 商品 9900005456 默认配置 |
| `query-store-coupons` | 成功，返回空数组 | 当前账户、门店与日期 |
| `calculate-price` | 成功，3800 分 | 单商品默认配置、无券 |

定义快照说明“知道接口怎样使用”；真实调用证据说明“在记录范围内执行成功”。两个层次分别陈述。

## 5. 八条任务路线与 35 项工具

| 路线 | 工具 |
|---|---|
| 点餐核价 6 项 | `query-nearby-stores`、`query-meals`、`query-meal-detail`、`query-store-coupons`、`calculate-price`、`create-order` |
| 账户优惠 5 项 | `query-my-account`、`query-my-coupons`、`available-coupons`、`campaign-calendar`、`auto-bind-coupons` |
| 订单售后 4 项 | `order-list`、`query-order`、`query-survey-coupon`、`cancel-order` |
| 外送地址 3 项 | `delivery-query-addresses`、`delivery-query-stores`、`delivery-create-address` |
| 团餐活动 7 项 | `query-meal-assistance`、`query-promotions`、`query-party-city`、`query-party-store`、`query-party-store-date`、`query-party-store-session`、`party-order-create` |
| 积分商城 5 项 | `mall-points-products`、`mall-product-detail`、`mall-order-list`、`mall-order-detail`、`mall-create-order` |
| 抽奖奖品 3 项 | `query-lottery-info`、`query-my-prizes`、`draw-lottery` |
| 营养时间 2 项 | `list-nutrition-foods`、`now-time-info` |

其中 28 项属于读取、时间或核价；7 项会改变账户、地址、抽奖、订单或积分状态。

## 6. 当前发布门控

当前运行 Skill 使用 `WRITE_MODE=GUIDE_ONLY` 管理七项状态变更工具：

| 工具 | 可能改变的状态 | 当前处理 |
|---|---|---|
| `auto-bind-coupons` | 账户优惠券 | 展示可领券与官方领取路径 |
| `cancel-order` | 订单状态 | 生成订单、原因与影响确认摘要 |
| `create-order` | 标准订单 | 生成绑定报价快照的官方渠道清单 |
| `delivery-create-address` | 账户地址 | 生成最小字段清单，用户在官方渠道保存 |
| `draw-lottery` | 抽奖机会或资源 | 先展示资格与下一次消耗，再交回用户 |
| `mall-create-order` | 积分与商城订单 | 展示商品、数量、地址与积分确认摘要 |
| `party-order-create` | 活动订单 | 展示城市、门店、日期、场次与人数确认摘要 |

这七项在当前版本中只负责“解释、准备、交接”。最终动作由用户在麦当劳官方渠道亲自完成。

账户、地址、订单、奖品与权益读取采用 `ON_INTENT`：用户明确提出相应任务后，Skill 说明读取类别，再调用最短工具链，输出只保留完成任务所需的最少信息。

## 7. 核心点餐快线

历史有限实测的主链为：

~~~text
query-nearby-stores
→ query-meals
→ query-meal-detail
→ query-store-coupons
→ calculate-price
→ 用户继续修改 / 生成“未下单”沟通卡 / 转官方渠道
~~~

关键合同：

- 到店自取：`beType=1, orderType=1`，`beCode` 留空
- 得来速：`beType=5, orderType=1`，`beCode` 来自 `query-nearby-stores`
- 麦乐送：`beType=2, orderType=2`，`addressId` 与 `beCode` 来自外送路线
- 企业团餐：`beType=6, orderType=2`，`gmServiceCode` 来自 `query-meal-assistance`
- 预约：`reservationDate` 只随预约场景传递
- 特调：含 `unselectedKey` 的组按真实详情全量回传选择状态
- 金额：内部统一使用整数分；对外显示两位小数人民币元
- 报价绑定门店、通道、餐品、数量、套餐选项、优惠与时间；任一绑定项变化即进入 `STALE`

## 8. 条件依赖高于表面字段数

- `query-nearby-stores.searchType=2` 同时需要 `city` 与 `keyword`。
- `create-order` 的顶层 Schema 只要求三个字段，实际还要按通道取得 `takeWayCode`、`addressId` 或 `gmServiceCode`。
- `party-order-create` 的顶层 Schema 只要求 `partyType`，业务链还需要从积分商品、城市、门店、日期与场次真实返回中逐项取得标识和人数。
- `mall-create-order` 处理实体商品时还需要用户选择的 `addressId`。
- `draw-lottery` 先读取资格、资源条件与下一次消耗。
- `query-meal-assistance` 的“助餐服务”属于企业团餐业务语义，与无障碍辅助功能分开表述。
- `list-nutrition-foods` 提供官方营养信息；过敏、疾病、孕期与治疗饮食由用户结合官方信息和专业意见判断。

## 9. 输出与异常恢复

35 项定义都缺少 `outputSchema` 与 `annotations`，因此输出解析采用当前真实返回：

- 字段存在时记录字段值与查询时间
- 字段缺失或结构变化时标为 `UNKNOWN`
- 401 时引导用户在本机检查 Token
- 429 时停止连续调用并约定稍后重试
- 网络中断时保留草稿和上次成功时间
- 菜单、通道或报价变化时重新查询和核价
- 状态变更结果由官方渠道回执确认

## 10. 对个人与企业的实际价值

对个人，八条路线把自然语言变成一条可看懂、可修改、可停止的任务链；预算、数量、排除项与状态始终清楚。对企业，工具地图帮助团队看见哪些步骤容易产生误解、重复确认与服务中断，进而开展匿名流程评估、员工话术设计和无障碍共创。

效果指标继续由取得同意的真实研究产生。定义数量、图片数量与工具调用次数都只属于工程事实，继续与用户效果分别报告。
