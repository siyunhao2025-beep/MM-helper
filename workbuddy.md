# WorkBuddy 开发上下文（workbuddy.md）

> **文件性质**：本文件是从真实 WorkBuddy 会话整理出的**结构化**上下文，每条记录均带时间戳、工具名、traceId 或产物哈希，可逐项对账。它用于核验「本项目真实使用腾讯 WorkBuddy 开发麦当劳 MCP Skill」。
> 已脱敏：全文不含 Token、密钥、手机号、收货地址、支付信息或他人个人信息。

## 1. 开发环境（真实）

| 项 | 值 |
|---|---|
| 工具 | WorkBuddy 桌面版（本次比赛的官方合作工具） |
| 时间跨度 | 2026-10-09 起，最新记录 2026-10-10 |
| MCP 连接器 | `mcd-mcp`（WorkBuddy 自定义连接器，已启用） |
| MCP Server | 麦当劳中国官方 MCP，`https://mcp.mcd.cn`，Streamable HTTP |
| 认证 | Bearer Token；凭证保存在本机受保护配置，从未进入仓库、日志或本文件 |
| 服务范围 | 中国大陆地区；港澳台位于当前服务范围外 |
| 账户边界 | Token 与个人会员账号绑定，服务本人、个人用途与正常频率交互 |

## 2. 真实 MCP 调用记录（6 项，均带 traceId）

来源：`docs/EVIDENCE_LEDGER.jsonl` E1–E6。全部为只读或核价调用，**没有任何状态变更调用**。

| 时间 (GMT+8) | 工具 | 调用参数 | 真实返回 | traceId |
|---|---|---|---|---|
| 10-09 15:34:29 | `query-my-account` | 无参 | `availablePoint=0`；`accumulativePoint=199.9`；`expiredPoint=199.9` | `f2a5c0be25b8b87ee1289978062e426d` |
| 10-09 17:05:31 | `query-nearby-stores` | `searchType=2, city=珠海, keyword=拱北口岸, beType=1` | 5 家门店（1440032 来魅力口岸城 298m 等）；`beType=1` 返回无 `beCode`；含营业时间与 `reservationTimeOptions` | `499b328d14a2486d5cfe23fe238fbf02` |
| 10-09 17:05:40 | `query-meals` | `storeCode=1440032, orderType=1, beType=1` | 13 分类约 90 个商品；`data.meals` 为 code→详情映射（名称/图片/现价/原价） | `6127fb295975dece95a234be07bf1fa1` |
| 10-09 17:05:53 | `query-meal-detail` | `storeCode=1440032, orderType=1, beType=1, code=9900005456` | 3 个 round（汉堡/小食/饮料）；默认中薯条+可乐中杯；特调组含 `selectedKey`/`unselectedKey`；差价字段 `diffPrice` | `a113b4cc956ba05cebd2e2e6de22d590` |
| 10-09 17:05:53 | `query-store-coupons` | `storeCode=1440032, orderType=1, beType=1` | `data=[]`（该账户该门店此时无可用券，属正常态） | `aaeadd918889cad31e37c4294cc97335` |
| 10-09 17:06:09 | `calculate-price` | `storeCode=1440032, orderType=1, beType=1, items=[{productCode=9900005456, quantity=1}]` | `price=3800` 分（=38.00 元，与菜单现价一致）；`discount=0`；`takeWayList=[堂食 eat-in, 外带 take-in-store]` | `d6e351dd8023714f13fdbafdced0b994` |

**边界声明**：这 6 项只证明「在记录范围内执行成功」。其余 29 项工具仍缺真实执行回执，不在本表内。

## 3. WorkBuddy 中的工具定义采集（2026-10-10 11:14）

在 WorkBuddy 会话中对 `mcd-mcp` 做了一次**纯元数据采集**，产出五个文件：raw JSON、catalog JSONL、matrix Markdown、capture report、SHA-256 清单。

| 校验项 | 结果 |
|---|---:|
| 工具总数 | 35 |
| JSONL 记录数 | 35 |
| 唯一运行时名称 | 35 |
| 名称 / 描述 / inputSchema 逐项对齐 | 35 / 35 / 35 / 35 |
| schema SHA-256 可复算 | 35 / 35 |
| 本次业务工具调用次数 | **0** |
| 本次状态变更次数 | **0** |
| Token 与真实个人数据扫描 | **0** 命中 |

采集来源：`WORKBUDDY_INJECTED_METADATA`——WorkBuddy 向会话注入了工具定义。本轮未取得原始 `tools/list` 响应，`outputSchema` 与 `annotations` 运行时均未提供（35/35 为 null），这些事实边界已原样保留在采集报告中。

产物哈希：

- `01-mcd-tools-raw.json`：`a97406cb3438268b28aef9e1c64e6e6113fc47c2b6752b9b9991da3ab5219413`
- `02-mcd-tools-catalog.jsonl`：`92fea9c0e31248c628531784364cad15cab541133e44df8e0ac5d1107ce36d57`
- `03-mcd-tools-matrix.md`：`4617b70bffd537823c836d7f90e81cdefef93136fe629fd25bfefc8262c0e6c9`
- `04-mcd-tools-capture-report.md`：`9a3eb7e171c316c0426d7c5103902c692a93f29a09e15c8e90b7a102ca12ce0b`

## 4. 2026-10-10 下午会话：Skill 安装与比赛规则复核

| 时间 (GMT+8) | 在 WorkBuddy 中做的事 | 可核验结果 |
|---|---|---|
| 13:09 | 从 GitHub 拉取 `siyunhao2025-beep/MM-helper`，对两个 Skill 做安全审计后安装到 WorkBuddy 用户级技能目录 | 仅含一个脚本 `validate_contracts.py`，纯标准库只读，无网络、子进程或写文件行为；审计通过 |
| 13:14 | 在完整仓库根目录运行仓库自检 | `PASS: 118 checks` |
| 13:25 | 重新核验比赛规则文件 | README / activityGuidelines / CONTEST_DECLARATION / RANKING 四份已逐份读取核对 |
| 13:27 | 比对 `CONTEST_DECLARATION.md` 与官方原文 | git blob SHA-1 同为 `136e76f3160317049f19f5ba03f4d0fedd70fc3c`，**字节级一致** |
| 13:30 | 核实报名 Issue 提交地址 | `M-China-Official` 已 301 重定向至 `M-China`（repo id 1382852418），两者等价 |

## 5. 本次同步提交的变更

- 新增 `LICENSE`（MIT），替换原先「授权范围待明确」的状态
- 本文件由摘要版升级为带完整可核验要素的结构化版本
- `README.md` 中两处许可证状态描述同步更新

## 6. 需求来源

主提示词《慢慢点 WorkBuddy 完整执行提示词（单文件整合版 v1.0）》由项目作者提供，SHA-256 `658b016c…c2fa6`。

## 7. 边界重申

本项目是独立开发的参赛作品，属于第三方创作，代表作者个人立场，与麦当劳官方产品保持区分。7 项状态变更工具（`create-order`、`cancel-order`、`auto-bind-coupons`、`delivery-create-address`、`draw-lottery`、`mall-create-order`、`party-order-create`）在本版本中一律 `WRITE_MODE=GUIDE_ONLY`，只负责解释、准备与确认摘要，最终动作由用户在麦当劳官方渠道亲自完成。
