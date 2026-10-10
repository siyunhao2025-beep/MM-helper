# MCP_CAPABILITY_MATRIX — 35 工具能力矩阵

> 更新时间：2026-10-10（北京时间）。本表分别记录定义快照、本次采集执行状态与历史真实证据。“取得 Schema”只证明接口契约可见；“真实执行”需要本次或历史回执。证据索引见 `docs/EVIDENCE_LEDGER.jsonl`。

## 证据口径

- **E18 元数据快照**：WorkBuddy 注入的 35 项工具定义；名称、描述、输入 Schema 与哈希均完成交叉校验。
- **本次真实执行**：采集会话业务调用 0 次、状态变更调用 0 次，因此 35 项统一为 `NOT_TESTED`。
- **E1–E6 历史实测**：2026-10-09 的一个账户、珠海门店与单商品有限样例，共 6 项。
- **当前模式**：
  - `CORE_READ`：日常点餐快线。
  - `ON_INTENT`：用户提出对应任务后读取。
  - `ON_CONTEXT`：当前任务确有时间上下文时读取。
  - `GUIDE_ONLY`：准备依赖项与确认摘要，状态变更交回麦当劳官方渠道。

当日官方公开工具表有 33 项；运行时另有 `query-promotions`、`query-survey-coupon`。派对日期与场次的运行时短名为 `query-party-store-date`、`query-party-store-session`，与公开表的 `query-partystore-*` 写法存在差异。真实调用以当前运行时名称为准。

## 逐工具矩阵

| # | 工具短名 | 路线 | Schema | 本次采集执行 | 历史真实执行 | 当前模式 | 关键依赖 |
|---:|---|---|---|---|---|---|---|
| 01 | `auto-bind-coupons` | 账户优惠 | ✅ E18 | 0 次 | — | `GUIDE_ONLY` | 本人账户；先展示可领券 |
| 02 | `available-coupons` | 账户优惠 | ✅ E18 | 0 次 | — | `ON_INTENT` | 本人账户 |
| 03 | `calculate-price` | 点餐核价 | ✅ E18 | 0 次 | ✅ E6 | `CORE_READ` | 门店、通道、餐品与选项 |
| 04 | `campaign-calendar` | 账户优惠 | ✅ E18 | 0 次 | — | `ON_INTENT` | 指定日期可选；结果可能含订阅状态 |
| 05 | `cancel-order` | 订单售后 | ✅ E18 | 0 次 | — | `GUIDE_ONLY` | 真实 `orderId` 与原因代码 |
| 06 | `create-order` | 点餐核价 | ✅ E18 | 0 次 | — | `GUIDE_ONLY` | 最新报价快照与通道条件字段 |
| 07 | `delivery-create-address` | 外送地址 | ✅ E18 | 0 次 | — | `GUIDE_ONLY` | 地址、门牌、城市、联系人、手机号 |
| 08 | `delivery-query-addresses` | 外送地址 | ✅ E18 | 0 次 | — | `ON_INTENT` | 本人账户地址 |
| 09 | `delivery-query-stores` | 外送地址 | ✅ E18 | 0 次 | — | `ON_INTENT` | `addressId` + `beType=2/6` |
| 10 | `draw-lottery` | 抽奖奖品 | ✅ E18 | 0 次 | — | `GUIDE_ONLY` | 先读资格、资源与下一次消耗 |
| 11 | `list-nutrition-foods` | 营养时间 | ✅ E18 | 0 次 | — | `ON_INTENT` | 官方营养信息语境 |
| 12 | `mall-create-order` | 积分商城 | ✅ E18 | 0 次 | — | `GUIDE_ONLY` | `skuId`、分类、积分；实体商品含地址 |
| 13 | `mall-order-detail` | 积分商城 | ✅ E18 | 0 次 | — | `ON_INTENT` | 商城 `orderId` |
| 14 | `mall-order-list` | 积分商城 | ✅ E18 | 0 次 | — | `ON_INTENT` | 本人账户；分页可选 |
| 15 | `mall-points-products` | 积分商城 | ✅ E18 | 0 次 | — | `ON_INTENT` | 分类规则可选 |
| 16 | `mall-product-detail` | 积分商城 | ✅ E18 | 0 次 | — | `ON_INTENT` | `spuId` |
| 17 | `now-time-info` | 营养时间 | ✅ E18 | 0 次 | — | `ON_CONTEXT` | 当前时间确有业务影响 |
| 18 | `order-list` | 订单售后 | ✅ E18 | 0 次 | — | `ON_INTENT` | 本人账户订单 |
| 19 | `party-order-create` | 团餐活动 | ✅ E18 | 0 次 | — | `GUIDE_ONLY` | 商品→城市→门店→日期→场次→人数 |
| 20 | `query-lottery-info` | 抽奖奖品 | ✅ E18 | 0 次 | — | `ON_INTENT` | 本人资格与资源 |
| 21 | `query-meal-assistance` | 团餐活动 | ✅ E18 | 0 次 | — | `ON_INTENT` | `beType=6`；配送门店与 `beCode` |
| 22 | `query-meal-detail` | 点餐核价 | ✅ E18 | 0 次 | ✅ E4 | `CORE_READ` | 门店、通道、餐品 `code` |
| 23 | `query-meals` | 点餐核价 | ✅ E18 | 0 次 | ✅ E3 | `CORE_READ` | 门店与通道 |
| 24 | `query-my-account` | 账户优惠 | ✅ E18 | 0 次 | ✅ E1 | `ON_INTENT` | 本人账户 |
| 25 | `query-my-coupons` | 账户优惠 | ✅ E18 | 0 次 | — | `ON_INTENT` | 本人已有券；分页可选 |
| 26 | `query-my-prizes` | 抽奖奖品 | ✅ E18 | 0 次 | — | `ON_INTENT` | 本人奖品；分页可选 |
| 27 | `query-nearby-stores` | 点餐核价 | ✅ E18 | 0 次 | ✅ E2 | `CORE_READ` | `beType`、搜索类型；关键词搜索含城市 |
| 28 | `query-order` | 订单售后 | ✅ E18 | 0 次 | — | `ON_INTENT` | 真实 `orderId` |
| 29 | `query-party-city` | 团餐活动 | ✅ E18 | 0 次 | — | `ON_INTENT` | 积分商品 `spuId` |
| 30 | `query-party-store` | 团餐活动 | ✅ E18 | 0 次 | — | `ON_INTENT` | 城市 `code`；经纬度与 `spuId` |
| 31 | `query-party-store-date` | 团餐活动 | ✅ E18 | 0 次 | — | `ON_INTENT` | `spuId` + `storeCode` |
| 32 | `query-party-store-session` | 团餐活动 | ✅ E18 | 0 次 | — | `ON_INTENT` | 商品、门店与 `dateStr` |
| 33 | `query-promotions` | 团餐活动 | ✅ E18 | 0 次 | — | `ON_INTENT` | `beType=6, orderType=2` + `beCode` |
| 34 | `query-store-coupons` | 点餐核价 | ✅ E18 | 0 次 | ✅ E5（空数组） | `CORE_READ` | 门店与通道 |
| 35 | `query-survey-coupon` | 订单售后 | ✅ E18 | 0 次 | — | `ON_INTENT` | 用户指定的 `orderId` |

## 已验证的核心接口合同

1. 到店自取：`beType=1 + orderType=1`，`beCode` 留空；得来速 `beType=5` 的 `beCode` 来自门店查询。
2. 特调选项：含 `unselectedKey` 的组按真实详情全量回传选择状态。
3. 金额单位为整数分；展示时换算成人民币元并保留两位小数。
4. `minValues=1, maxValues=1` 的特调组要求选择一项。
5. 优惠券空数组代表该账户在该门店本次返回 0 张可用券。
6. `reservation=true` 的门店可返回 `reservationTimeOptions`，预约时间由用户选择。

## 从 35 项定义新增确认的条件合同

1. 四种通道：自取 `1/1`、得来速 `5/1`、麦乐送 `2/2`、企业团餐 `6/2`，依次表示 `beType/orderType`。
2. `query-nearby-stores.searchType=2` 需要 `city + keyword`。
3. 团餐先由 `delivery-query-stores` 取得 `storeCode/beCode`，再查询助餐服务与团餐促销。
4. `query-promotions` 只适用于 `beType=6, orderType=2`。
5. 派对下单的 Schema 表面必填只有 `partyType`，业务语义还要求商品、城市、门店、日期、场次与人数全链标识。
6. 抽奖先查询资格与资源条件；积分实体商品还需地址。
7. 全部 35 项均缺少 `outputSchema` 与 `annotations`，输出字段以本次真实返回为准。

## 当前证据边界

- E1–E6 只覆盖一个账户、珠海拱北 5 家门店中的单店、一个商品默认配置与无券核价。
- 得来速、外送、团餐、预约、非默认特调、券应用、积分商城、派对、抽奖、订单售后仍待有限、合规、逐项验证。
- 7 个状态变更工具当前为 `GUIDE_ONLY`，本仓库没有状态变更调用证据。
- 工具定义会演进；每次调用继续以当前运行时名称、Schema 与真实返回为准。
