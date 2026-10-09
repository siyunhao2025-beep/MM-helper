# MCP_INTEGRATION — 麦当劳 MCP 真实集成说明

> 本文件说明本项目实际使用的麦当劳 MCP Server、Tool、调用流程和业务价值。所有「已验证」条目均有真实调用证据（traceId 与时间戳），索引见 docs/EVIDENCE_LEDGER.jsonl 与 docs/MCP_CAPABILITY_MATRIX.md。

## 1. 服务器与连接

- Server：麦当劳中国官方 MCP（https://mcp.mcd.cn ，streamablehttp）
- 认证：Bearer Token（用户在 open.mcd.cn/mcp 自助申请；仓库只保存环境变量占位示例 mcp-config.example.json）
- 账户能力：35 个工具（真实 tools/list 采集，2026-10-09）

## 2. 本项目使用的工具与真实状态

| 工具 | 用途 | 文档支持 | schema 获取 | 真实只读执行 | 真实写入执行 |
|---|---|---|---|---|---|
| query-nearby-stores | 按地点查门店 | 是 | 是 | 是（2026-10-09） | — |
| query-meals | 当前门店菜单 | 是 | 是 | 是（2026-10-09） | — |
| query-meal-detail | 套餐组成与可替换项 | 是 | 是 | 是（2026-10-09） | — |
| query-store-coupons | 门店适用优惠（不自动领券） | 是 | 是 | 是（2026-10-09，空返回=无券） | — |
| calculate-price | 草稿核价 | 是 | 是 | 是（2026-10-09） | — |
| create-order | 创建订单 | 是 | 是 | 未执行 | 未执行（需独立授权+代码门禁） |
| query-order / order-list | 订单状态核验 | 是 | 是 | 未执行 | 未执行 |
| cancel-order | 取消订单 | 是 | 是 | 未执行 | 未执行（单独授权） |

## 3. 实际调用流程（只读链，已真实验证）

1. query-nearby-stores(searchType=2, city, keyword, beType=1) → storeCode
2. query-meals(storeCode, orderType=1, beType=1) → 商品 code 与现价
3. query-meal-detail(storeCode, orderType=1, beType=1, code) → rounds / choices / modification
4. query-store-coupons(storeCode, orderType=1, beType=1) → couponId / couponCode（可为空）
5. calculate-price(storeCode, orderType=1, beType=1, items) → 总价

真实关键参数规则（来自真实 schema 与实测，非猜测）：

- 到店自取（beType=1 / orderType=1）不传 beCode，传了会报错；得来速（beType=5）必传 beCode
- 特调选项：含 unselectedKey 的组必须全量回传——选中项用 selectedKey、未选中项用 unselectedKey
- 金额一律以「分」返回，展示时除以 100；内部计算使用整数分，不让大模型心算
- reservation=true 的门店必须完整展示 reservationTimeOptions

## 4. 业务价值

真实菜单与核价让候选、总价与未知项都有官方来源；未下单沟通卡、订单待核实卡、官方取餐提示三类卡片分离，减少「以为已下单」与重复购买。收益指标设计见主提示词第 18 节；尚未开展用户研究，不预填成绩。

## 5. 只读/写入边界与异常恢复

- 本项目当前为真实只读：create-order / cancel-order 未执行；写操作须通过独立确认门禁（快照绑定全要素、防并发防重、创建未知→核验不重下）
- 401 → 提示连接核验，不泄露 Token，不无限重试；429 → 有界退避
- 报价过期 → 保留草稿重新核价，不催促付款
- 网络断开 → 明示离线与缓存时间，禁用未经核价的写入
