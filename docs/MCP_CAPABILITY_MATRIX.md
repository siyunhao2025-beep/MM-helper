# MCP_CAPABILITY_MATRIX — 工具能力矩阵

> 逐工具记录从文档到实际调用的状态；未测试工具不得标“已接入”。证据索引见 docs/EVIDENCE_LEDGER.jsonl。采集环境：WorkBuddy 会话 + 官方 mcd.cn MCP（Bearer Token，本地受保护），2026-10-09。服务范围按官方规则为中国大陆地区（不含港澳台）；下表是历史时点观测，不代表工具总数或所有门店长期不变。

| 工具 | 文档支持 | 账户发现(tools/list) | schema 获取 | 真实只读执行 | 真实写入执行 | 依赖条件 | 证据 |
|---|---|---|---|---|---|---|---|
| query-my-account | ✅ | ✅ | ✅ | ✅ 2026-10-09 15:34 | — | 已连接 MCP | E1 |
| query-nearby-stores | ✅ | ✅ | ✅ | ✅ 2026-10-09 17:05 | — | 用户提供地点；beType 明确 | E2 |
| query-meals | ✅ | ✅ | ✅ | ✅ 2026-10-09 17:05 | — | storeCode + beType/orderType | E3 |
| query-meal-detail | ✅ | ✅ | ✅ | ✅ 2026-10-09 17:05 | — | 商品 code | E4 |
| query-store-coupons | ✅ | ✅ | ✅ | ✅ 2026-10-09 17:05（空返回） | — | storeCode | E5 |
| calculate-price | ✅ | ✅ | ✅ | ✅ 2026-10-09 17:06 | — | items（productCode+quantity） | E6 |
| campaign-calendar | ✅ | ✅ | ✅ | 未执行 | — | — | — |
| create-order | ✅ | ✅ | ✅ | — | ⛔ 未执行 | 用户具体授权 + 代码门禁（快照绑定/防并发/未知不重下） | — |
| query-order / order-list | ✅ | ✅ | ✅ | 未执行 | 未执行 | 可靠订单标识 | — |
| cancel-order | ✅ | ✅ | ✅ | — | ⛔ 未执行 | 单独授权 + 真实可取消状态 | — |
| delivery-* / party-* / mall-* / lottery 等 | ✅ | ✅ | ✅ | 未执行 | 未执行 | 不进入默认流程（外送/团餐/积分兑换为后续扩展） | — |

## 已验证的关键接口合同（真实 schema + 实测，非猜测）

1. 到店自取：beType=1 + orderType=1，**不传 beCode**（传了报错）；得来速 beType=5 必传 beCode（来自 query-nearby-stores 返回）
2. 特调选项：含 unselectedKey 的组必须全量回传算价——选中项 key=selectedKey，未选中项 key=unselectedKey
3. 金额单位一律为**分**；calculate-price 返回 price/discount/originalPrice/productList/takeWayList（堂食 eat-in / 外带 take-in-store）
4. minValues=1 且 maxValues=1 的特调组为必选，不得提供"不选"
5. 优惠券空数组 = 该账户该门店无可用券（正常态）
6. reservation=true 门店返回 reservationTimeOptions 全量时段（today 标记当天）

## 已验证范围与限制

- 范围：珠海拱北 5 家门店、门店 1440032、商品 9900005456（默认配置）；单次调用成功不代表所有门店/日期/订单情形通过
- 未测：得来速、外送、预约场景、特调非默认配置计价、券应用计价
- 使用边界：Token 与个人会员账号绑定，仅限本人、非商业、正常交互；不得将这些工具接入企业代客、批量、高频或无人值守流程
