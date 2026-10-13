# 决定权护栏与报价契约

需要筛候选、处理约束冲突、比较优惠、重新核价或生成沟通卡时读取本文件。工具字段继续以当前运行时 Schema 为准。

## 目录

1. 事实入口
2. 候选三态
3. 排序与冲突说明
4. 报价绑定
5. 优惠比较
6. 状态变更路线
7. 确定性校验器
8. 最小结构化输入

## 1. 事实入口

只接受以下来源：

- `USER_PROVIDED`：预算、人数、想要、排除项、操作偏好。
- `TOOL_OBSERVED`：本轮 MCP 返回的门店、菜单、详情、优惠与核价。
- `DOC_CONFIRMED`：官方文件明确写明的规则。
- `TEST_OBSERVED`：仓库测试夹具与自动测试，只证明对应测试范围。
- `INFERENCE`：基于已知字段的低风险归纳，对外明确标为判断。
- `UNKNOWN`：可靠字段仍待取得，并附下一步核实动作。

测试夹具统一写 `TEST_FIXTURE`；真实工具回执统一写 `TOOL_OBSERVED`。两个标签各自独立。每份报价与每个带核价的候选同时提供事实类型和证据摘要：

| 证据模式 | 动态价格事实类型 | 证据摘要示例 |
|---|---|---|
| `TEST_FIXTURE` | `TEST_OBSERVED` | 测试夹具中的 calculate-price 响应 |
| `TOOL_OBSERVED` | `TOOL_OBSERVED` | 本轮 calculate-price 回执与查询时间 |

模式与动态事实类型一致后再进入候选与预算计算。

顶层 `evaluated_at` 记录本次本地复核时间。所有 `observed_at` 使用带时区 RFC3339，并早于或等于 `evaluated_at`。`freshness=CURRENT / EXPIRED / UNKNOWN` 是适配层依据本轮回执给出的显式断言；本地核心校验格式、先后关系与状态联动。官方回执提供 `validUntil` 时由适配层优先采用；官方回执只提供观察时间时，适配层在本次紧邻核价的复核中给出 `CURRENT`，跨会话恢复采用 `UNKNOWN` 并重新核价。

对价格、营养、历史与优惠结论，优先保留一组证据字段：`source`、`observed_at`、`store + fulfillment`、`coverage`、`verification`。空列表、列表缺席、解析失败和工具失败采用各自状态；部分覆盖展示“已匹配 X / 总计 Y”，汇总值标为已匹配部分下界。

## 2. 候选三态

草稿把用户明确说出的“必须、上限、至少、避开”写进 `required_constraints`：

```json
{
  "required_constraints": [
    {"id": "must-chicken-main", "user_text": "包含鸡肉主食"},
    {"id": "avoid-spicy", "user_text": "辣味"}
  ]
}
```

`id` 在本次草稿内保持稳定，`user_text` 原样保存。`wants` 默认作为软偏好；用户明确提升为硬要求时，同时加入 `required_constraints`。每个候选用同一 `constraint_id` 逐项回应。遗漏项由本地核心补为 `HARD + UNKNOWN`，排除项也自动进入硬约束清单。

每个候选对每项约束只能采用一种状态：

| 状态 | 含义 | 展示方式 |
|---|---|---|
| `PASS` | 当前证据明确支持 | 已确认符合 |
| `FAIL` | 当前证据明确冲突 | 说明冲突并移出推荐位 |
| `UNKNOWN` | 当前字段仍待取得 | 醒目标为待确认 |

硬约束的 `PASS` 与 `FAIL` 需要 `TOOL_OBSERVED`、`DOC_CONFIRMED` 或 `TEST_OBSERVED` 证据。推测只进入软偏好排序或 `UNKNOWN`。

## 3. 排序与冲突说明

先移出含硬约束 `FAIL` 的候选，再按以下顺序排列：

1. 硬约束待确认项更少。
2. 预算状态为 `WITHIN`。
3. 已确认硬约束更多。
4. 已确认软偏好更多。
5. 用户偏好分更高。
6. 核价更低，仅作为末级展示顺序。

首屏最多三个候选。每个候选都展示“已确认、待确认、核价、选择依据”。

当全部候选存在冲突时：

1. 列出冲突来自哪条用户原话。
2. 保留预算、数量与排除项原值。
3. 提供“保留原要求并换一批 / 调整一项 / 暂时结束”。
4. 由用户点名调整项后再生成新草稿。

这叫“最小调整建议”：系统负责解释代价，调整权始终属于用户。

## 4. 报价绑定

每份报价快照绑定：

```text
storeCode + 取餐方式 + 履约参数 + 商品编码 + 数量 + 选项 + 优惠标识 + pricing_request_sha256
```

以上字段经过排序与规范化后计算购物篮 SHA-256 指纹。当前草稿指纹与核价时指纹一致、来源工具为 `calculate-price`、报价新鲜度为 `CURRENT` 时，报价状态为 `VALID`。

履约参数使用当前官方路线：到店 `beType=1/orderType=1`；得来速 `5/1` 并绑定 `beCode`；麦乐送 `2/2` 并绑定 `addressId + beCode`；企业团餐 `6/2` 并绑定 `addressId + beCode + gmServiceCode`。预约与主题活动场次字段随对应路线进入指纹。取餐方式展示词与路线画像保持一致。

`pricing_request_sha256` 是调用方提供的绑定摘要。真实适配层完成后，它须按本轮运行时 Schema 规范化实际发出的完整 `calculate-price` 请求，再计算 SHA-256；摘要覆盖商品轮次、特调、优惠、`needTableware`、`withOrder` 以及当前 Schema 中其余核价字段。现有本地核心把该摘要视为信任边界，只校验 64 位十六进制格式、绑定与变化关系；它并未重建完整请求。结构化外壳采用字段白名单，游离字段进入结构化错误。公开报告只写 `pricing_request_bound=true`；地址只写 `address_bound=true`；优惠只写绑定数量。

商品展示名服务于阅读，商品编码负责绑定；展示名变化保持报价有效，商品编码、数量或选项变化触发新指纹。

商品和选项都采用编码与展示名分离：

```json
{
  "code": "MEAL_CODE",
  "name": "本轮官方展示名",
  "quantity": 1,
  "options": [
    {"code": "OPTION_CODE", "name": "本轮官方选项名"}
  ]
}
```

指纹只采用商品编码、选项编码和数量；卡片优先展示本轮核价回执中的名称。草稿名与回执名各异时，`display_deltas` 只展示旧名称与本轮名称，让食客看见名称更新，交易编码继续留在内部绑定结构。

候选核价同时携带 `price_source_tool=calculate-price`、`price_observed_at`、`price_freshness`、`price_fact_type`、`price_evidence` 与完整 `price_binding`。`price_binding` 含履约参数与 `pricing_request_sha256`。带价候选的 `price_freshness` 处于 `EXPIRED` 或 `UNKNOWN` 时，候选转为 `PENDING`，金额只展示为历史参考价，排序等待新核价。

任一绑定字段变化后：

- 旧报价转为 `STALE`。
- 草稿回到 `DRAFT`。
- 总额显示“待重新核价”。
- 新报价返回后再进入 `QUOTED`。

金额在内部统一使用整数分；对外展示人民币元与两位小数。

## 5. 优惠比较

先比较购物篮，再比较金额：

- 商品编码、数量和选项一致：标为 `EQUIVALENT_BASKET`，可以展示经核价确认的节省金额。
- 商品、数量或选项变化：标为 `CHANGED_BASKET`，分别展示新总额、增加项、减少项与金额变化；公开变化清单使用本轮展示名，交易编码只参与内部比较。

两份方案各自提供门店、取餐方式、履约参数、商品、选项、优惠标识、`pricing_request_sha256`、`pricing_basis_sha256`、`source_tool`、`observed_at`、`freshness`、`fact_type` 与 `evidence`。`pricing_basis_sha256` 由真实适配层在精确请求中只中和明确的券字段后计算。商品签名或履约参数变化时，两类摘要同步变化；同名商品发生交易项替换时，公开文本提醒食客前往官方详情核对，交易码继续留在内部比较。门店或履约上下文各异时标为 `DIFFERENT_CONTEXT`；任一报价的新鲜度仍待确认时标为 `STALE_EVIDENCE`；同一清单里出现其余请求差异时标为 `DIFFERENT_PRICING_REQUEST`。只有同场景、同一清单、同一比较基准、两份当前核价形成 `verified_saving_fen`。优惠数量差异与核价请求摘要变化同步展示。

“为了用券多买一件”属于 `CHANGED_BASKET`。系统完整展示变化，食客判断新增商品是否值得。

## 6. 状态变更路线

以下七项工具统一返回 `GUIDE_ONLY`：

```text
auto-bind-coupons
cancel-order
create-order
delivery-create-address
draw-lottery
mall-create-order
party-order-create
```

本地代码只准备依赖清单、报价摘要和确认要点。领取、创建、取消、保存、抽奖与兑换动作由用户进入官方渠道逐项完成。

本地代码同时保存当前 35 项工具白名单：28 项读取、时间与核价工具返回 `CURRENT_SCHEMA_REQUIRED`，以上 7 项返回 `GUIDE_ONLY`，白名单外名称返回 `UNAVAILABLE_THIS_SESSION`。运行时出现新工具时，先核对当前 Schema、用途与副作用，再更新白名单和测试。

## 7. 确定性校验器

仓库提供零依赖代码：

```text
src/core/decision_guard.py
```

使用测试夹具运行：

```bash
python -m src.core.cli examples/accessible-order.fixture.json
python -m unittest discover -s tests -v
```

校验器覆盖：

- 整数分金额。
- 购物篮指纹与报价失效。
- 四类履约画像、路线必填项与展示词一致性。
- 调用方核价请求摘要格式与变化绑定、结构未知字段拦截与公开最小披露。
- 商品展示名与交易绑定字段分离。
- 测试夹具与真实工具证据模式隔离。
- 缺失价格保持 `UNKNOWN`，金额零值只由明确的整数分字段产生。
- 硬约束证据类型。
- 首屏最多三个候选。
- 同一清单优惠比较。
- 七项 `GUIDE_ONLY` 门控。
- 白名单外工具隔离。
- “尚未下单”报价卡。

- `selected_candidate_id` 与草稿、候选核价、当前报价三方绑定。
- 报价卡与沟通卡分别渲染，商品选项使用展示名。
- RFC3339 时间、复核时间与新鲜度联动。
- 读屏候选编号、数量、已确认、待确认与可说动作。
- 控制字符、双向控制符与孤立代理字符隔离。

它只处理本地结构化数据；MCP 调用仍由 WorkBuddy 连接器按本轮真实 Schema 执行。

## 8. 最小结构化输入

顶层字段：

| 字段 | 作用 |
|---|---|
| `evidence_mode` | `TEST_FIXTURE` 或 `TOOL_OBSERVED` |
| `evaluated_at` | 本次复核时间，带时区 RFC3339 |
| `response_mode` | 本地渲染器支持 `STANDARD`、`SCREEN_READER` |
| `draft` | 门店、取餐、履约参数、调用方核价请求摘要、预算、商品、优惠、硬约束与待确认项 |
| `quote` | 当前草稿的 `calculate-price` 报价与完整 `binding`，含履约参数与请求摘要 |
| `candidates` | 三态检查与逐候选核价 |
| `selected_candidate_id` | 用户当前点名的候选 |
| `card_requested` | 严格布尔值，控制报价卡 |
| `communication_card_requested` | 严格布尔值，控制文字沟通卡 |
| `offer_comparison` | 可选的基准与方案核价 |

交接卡生成条件：

```text
已选候选
+ 候选硬约束冲突为 0
+ 候选价格为 CURRENT
+ 候选购物篮指纹 = 当前草稿指纹
+ 候选总额 = 当前报价总额
+ 当前报价为 VALID
+ 当前预算状态位于 WITHIN 或 UNSET
```

硬约束 `UNKNOWN` 原样进入“请确认”；`HANDOFF_READY` 只表示卡片已经适合向本人或店员展示，交易状态仍为“尚未下单”。极简朗读由 `SCREEN_READER` 确定性渲染；安心慢选、文字沟通与直接比较继续采用无障碍回应模板，其中沟通卡由同一核心单独生成。

完整脱敏示例见 `examples/accessible-order.fixture.json`。
