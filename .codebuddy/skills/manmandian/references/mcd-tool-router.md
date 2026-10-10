# 麦当劳 MCP 35 工具路由手册

> 本手册供运行 Skill `manmandian` 按需读取。它把 2026-10-10 的 WorkBuddy 工具定义快照、2026-10-09 的有限范围真实调用证据和当前发布门控放在同一张地图上。

## 0. 先分清三件事

- **元数据已取得**：2026-10-10 采集到 35 个唯一运行时名称、35 份输入 Schema 和 35 个可复算的 Schema SHA-256。
- **本次采集为只读盘点**：业务工具调用 0 次，状态变更调用 0 次，全部 `live_test_status=NOT_TESTED`。
- **历史有限实测**：2026-10-09 的 E1–E6 记录了 6 个工具的真实返回；范围为一个账户和珠海单门店、单商品、默认配置样例，证据边界继续有效。

因此使用以下状态词：

| 状态 | 含义 |
|---|---|
| `METADATA_CAPTURED` | 名称与输入契约已取得 |
| `LIVE_VERIFIED_LIMITED` | 有限范围真实执行成功，范围见 E1–E6 |
| `ON_INTENT` | 仅在用户明确提出相关任务时调用 |
| `GUIDE_ONLY` | 当前版本负责解释流程与准备参数，实际状态变更交回官方渠道 |
| `UNKNOWN` | 当前返回或证据仍缺关键事实 |

机器可读契约见 `mcd-tool-contracts.json`；完整证据见仓库根目录 `docs/EVIDENCE_LEDGER.jsonl`。

## 1. 名称与事实优先级

调用前按以下顺序取事实：

1. 当前会话真实工具定义
2. 当前会话真实工具返回
3. 麦当劳当前官方指南与服务规则
4. 本目录的 2026-10-10 脱敏快照
5. 项目历史证据
6. 模型常识

当前 WorkBuddy 快照使用全名 `mcp__mcd-mcp__<short-name>`；界面可能显示 `<short-name>`。调用时先从当前工具清单解析真实全名，再按短名路由。

两处命名差异需要特别记住：

- 运行时为 `query-party-store-date` 与 `query-party-store-session`。
- 2026-10-10 查阅的官方公开工具表写作 `query-partystore-date` 与 `query-partystore-session`。

真实调用采用当前运行时名称。当前运行时还有 `query-promotions` 与 `query-survey-coupon`；当日官方公开工具表尚未列出这两项。工具总数属于时点快照，下一次会话继续动态发现。

## 2. 当前发布门控

- 28 个读取、时间与核价工具可按任务意图路由。
- 账户、地址、订单和权益读取采用 `ON_INTENT`，先说明将读取哪类信息，再取得用户本轮意图。
- 7 个状态变更工具统一采用 `WRITE_MODE=GUIDE_ONLY`：`auto-bind-coupons`、`cancel-order`、`create-order`、`delivery-create-address`、`draw-lottery`、`mall-create-order`、`party-order-create`。
- 状态变更流程只准备清单、依赖项和确认摘要；交易、地址保存、抽奖、领券与积分兑换由用户在麦当劳官方渠道亲自完成。
- 每次只走一条任务链，保持个人、正常频率交互。

## 3. 八条生活任务路线

| 用户要办的事 | 路由工具 | 结果交给谁决定 |
|---|---|---|
| 找店、看餐、改套餐、核价 | `query-nearby-stores` → `query-meals` → `query-meal-detail` → `query-store-coupons` → `calculate-price`；`create-order` 为引导态 | 食客选择门店、餐品、数量、优惠与购买渠道 |
| 看账户、券与当月活动 | `query-my-account`、`query-my-coupons`、`available-coupons`、`campaign-calendar`；`auto-bind-coupons` 为引导态 | 用户选择读取范围与领券动作 |
| 查订单与售后 | `order-list`、`query-order`、`query-survey-coupon`；`cancel-order` 为引导态 | 用户选择订单、评价入口与取消动作 |
| 准备外送 | `delivery-query-addresses` → `delivery-query-stores`；`delivery-create-address` 为引导态 | 用户选择地址、门店与外送方式 |
| 企业团餐与主题活动 | `query-meal-assistance`、`query-promotions`、`query-party-city`、`query-party-store`、`query-party-store-date`、`query-party-store-session`；`party-order-create` 为引导态 | 用户逐步选择服务、城市、门店、日期、场次与人数 |
| 看积分商城 | `mall-points-products`、`mall-product-detail`、`mall-order-list`、`mall-order-detail`；`mall-create-order` 为引导态 | 用户选择商品、数量、地址与兑换动作 |
| 看抽奖与奖品 | `query-lottery-info`、`query-my-prizes`；`draw-lottery` 为引导态 | 用户查看资格、消耗提示并亲自决定参与 |
| 看营养与当前时间 | `list-nutrition-foods`、`now-time-info` | 用户结合官方信息与专业意见作健康决定 |

“助餐服务”在工具语义中指企业团餐服务。它属于团餐路线，与无障碍辅助功能分别表述。

## 4. 35 项精确清单

全名统一为 `mcp__mcd-mcp__` 加表中短名。

| # | 短名 | 类别 | 必填字段 | 可选字段 | 当前模式 | 实测证据 |
|---:|---|---|---|---|---|---|
| 01 | `auto-bind-coupons` | 账户状态变更 | — | — | `GUIDE_ONLY` | — |
| 02 | `available-coupons` | 账户敏感读取 | — | — | `ON_INTENT` | — |
| 03 | `calculate-price` | 核价 | `storeCode, orderType, beType` | `beCode, gmServiceCode, items, needTableware, reservationDate, withOrder` | 核心读取 | E6 |
| 04 | `campaign-calendar` | 活动与订阅状态读取 | — | `specifiedDate` | `ON_INTENT` | — |
| 05 | `cancel-order` | 订单状态变更 | `orderId, cancelReasonCode` | — | `GUIDE_ONLY` | — |
| 06 | `create-order` | 创建订单 | `storeCode, orderType, beType` | `addressId, beCode, gmServiceCode, items, needTableware, remark, reservationDate, takeWayCode, withOrder` | `GUIDE_ONLY` | — |
| 07 | `delivery-create-address` | 地址状态变更 | `address, addressDetail, city, contactName, phone` | `gender` | `GUIDE_ONLY` | — |
| 08 | `delivery-query-addresses` | 地址读取 | — | — | `ON_INTENT` | — |
| 09 | `delivery-query-stores` | 外送门店读取 | `beType, addressId` | — | `ON_INTENT` | — |
| 10 | `draw-lottery` | 抽奖状态变更 | — | — | `GUIDE_ONLY` | — |
| 11 | `list-nutrition-foods` | 营养读取 | — | — | `ON_INTENT` | — |
| 12 | `mall-create-order` | 积分订单状态变更 | `skuId, spuCategory` | `addressId, count` | `GUIDE_ONLY` | — |
| 13 | `mall-order-detail` | 积分订单读取 | `orderId` | — | `ON_INTENT` | — |
| 14 | `mall-order-list` | 积分订单读取 | — | `lastId, size` | `ON_INTENT` | — |
| 15 | `mall-points-products` | 积分商品读取 | — | `catRuleIds` | `ON_INTENT` | — |
| 16 | `mall-product-detail` | 积分商品详情 | `spuId` | — | `ON_INTENT` | — |
| 17 | `now-time-info` | 时间上下文 | — | — | 按需读取 | — |
| 18 | `order-list` | 账户订单读取 | — | — | `ON_INTENT` | — |
| 19 | `party-order-create` | 活动订单状态变更 | `partyType` | `code, count, dateStr, id, leftNum, partyTimeInfo, skuId, spuId, storeCode, timeEnd, timeStart` | `GUIDE_ONLY` | — |
| 20 | `query-lottery-info` | 抽奖资格读取 | — | — | `ON_INTENT` | — |
| 21 | `query-meal-assistance` | 团餐助餐读取 | `storeCode` | `beCode, beType, orderType, reservationDate` | `ON_INTENT` | — |
| 22 | `query-meal-detail` | 餐品详情读取 | `storeCode, orderType, beType, code` | `beCode, reservationDate` | 核心读取 | E4 |
| 23 | `query-meals` | 门店菜单读取 | `storeCode, orderType, beType` | `beCode, reservationDate` | 核心读取 | E3 |
| 24 | `query-my-account` | 账户读取 | — | — | `ON_INTENT` | E1 |
| 25 | `query-my-coupons` | 已有券读取 | — | `page, pageSize` | `ON_INTENT` | — |
| 26 | `query-my-prizes` | 奖品读取 | — | `pageNum, pageSize` | `ON_INTENT` | — |
| 27 | `query-nearby-stores` | 门店读取 | `beType, searchType` | `city, keyword` | 核心读取 | E2 |
| 28 | `query-order` | 单笔订单读取 | `orderId` | — | `ON_INTENT` | — |
| 29 | `query-party-city` | 活动城市读取 | `spuId` | — | `ON_INTENT` | — |
| 30 | `query-party-store` | 活动门店读取 | `code` | `latitude, longitude, spuId` | `ON_INTENT` | — |
| 31 | `query-party-store-date` | 活动日期读取 | `spuId, storeCode` | — | `ON_INTENT` | — |
| 32 | `query-party-store-session` | 活动场次读取 | `spuId, storeCode, dateStr` | — | `ON_INTENT` | — |
| 33 | `query-promotions` | 团餐促销读取 | `storeCode, orderType, beType` | `beCode, reservationDate` | `ON_INTENT` | — |
| 34 | `query-store-coupons` | 门店适用券读取 | `orderType, beType, storeCode` | `beCode, reservationDate` | 核心读取 | E5 |
| 35 | `query-survey-coupon` | 订单问卷券读取 | `orderId` | — | `ON_INTENT` | — |

## 5. 四种点餐通道合同

| 场景 | `beType` | `orderType` | `beCode` 来源 | 额外条件 |
|---|---:|---:|---|---|
| 到店自取 | 1 | 1 | 留空 | 从 `calculate-price.takeWayList` 选择堂食或店内带走代码 |
| 得来速 | 5 | 1 | `query-nearby-stores` | 核价与后续动作持续绑定同一 `beCode` |
| 麦乐送 | 2 | 2 | `delivery-query-stores` | `addressId` 来自用户选择的地址 |
| 企业团餐 | 6 | 2 | `delivery-query-stores` | `gmServiceCode` 来自 `query-meal-assistance` |

- `reservationDate` 只随预约场景传递，格式遵循当前 Schema。
- `query-nearby-stores.searchType=2` 时同时提供 `city` 与 `keyword`。
- `query-promotions` 只服务 `beType=6, orderType=2` 的企业团餐路线。
- 门店、通道、餐品、数量、套餐选项、优惠任一项变化，旧报价进入 `STALE`，随后重新调用 `calculate-price`。

## 6. 条件必填与语义必填

JSON Schema 的顶层 `required` 只是第一层校验，还要执行工具描述中的条件依赖：

- `create-order`：到店类订单从核价结果取得 `takeWayCode`；外送类订单取得 `addressId`；团餐同时取得 `gmServiceCode`。当前版本只生成官方渠道确认清单。
- `party-order-create`：Schema 顶层只列 `partyType`，业务语义还要求从积分商品到城市、门店、日期、场次逐步取得 `spuId, skuId, code, storeCode, dateStr, id, timeStart, timeEnd, leftNum, count`，每一步都由用户明确选择。
- `mall-create-order`：实体商品 `spuCategory=2` 时取得用户选择的 `addressId`；积分余额与最终兑换结果以官方渠道为准。
- `draw-lottery`：先用 `query-lottery-info` 展示资格、资源条件和下一次消耗，再由用户亲自决定。
- `cancel-order`：只处理用户指定的真实 `orderId`，并在官方渠道展示当前可取消状态与原因代码。

## 7. 输出契约的证据边界

这批 35 项元数据均缺少 `outputSchema` 与 MCP `annotations`。因此：

1. 输入严格遵循当前运行时 Schema。
2. 输出只读取当前真实返回里存在的字段。
3. 字段缺失、结构变化或工具报错时使用 `UNKNOWN`，保留原草稿和调用时间。
4. 金额统一用整数分处理，展示为两位小数人民币元。
5. `list-nutrition-foods` 只提供官方营养信息；过敏、疾病、孕期与治疗饮食由用户结合官方餐品信息和专业意见判断。
6. 促销原始规则只用于解释符合条件的方案；用户原有需求、数量和预算保持优先。

## 8. 每次路由前的六问

1. 用户此刻要办哪一件事？
2. 这条路线需要公开读取、敏感读取，还是状态变更引导？
3. 当前会话真实工具名与 Schema 是什么？
4. 上游标识来自哪次真实返回？
5. 哪些字段是事实，哪些仍为 `UNKNOWN`？
6. 最终决定怎样清楚地交回用户？

六问答清后再调用工具；每次只推进一个主要动作。
