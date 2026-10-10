# THIRD_PARTY_NOTICES

## 本项目许可证

`LICENSE` 采用标准 MIT 文本。仓库所有者以该许可证授权其依法享有授权权利的原创贡献，包括 Skill 定义、脚本、文档与项目自制 SVG。第三方材料、商标与官方数据继续适用各自权利规则；本文件记录对应来源与边界。

版权行当前使用 GitHub 用户名 `siyunhao2025-beep`。作者可在报名或发布前确认继续使用该署名，或换成其希望公开的本名、机构名。

## 运行依赖与来源状态

当前（2026-10-10）校验脚本采用 Python 标准库；运行 Skill 依托 WorkBuddy 与麦当劳官方 MCP。README 使用四张 AI 生成概念插画和五张项目内确定性绘制的 SVG 信息图。仓库另含一份由 WorkBuddy 会话工具元数据派生的麦当劳 MCP 脱敏契约快照。

引入新代码、模型、数据集、字体、照片或图标包时，同步补充来源、版本、用途与再分发依据。

## 官方材料

- `CONTEST_DECLARATION.md`：内容来自麦当劳官方比赛仓库 M-China/mcd-developer-innovation-challenge（blob `136e76f3160317049f19f5ba03f4d0fedd70fc3c`），按官方要求逐字保留
- 比赛规则引用（`activityGuidelines.md` / `README.md`）：用于资格核验与事实摘要，版权归金拱门（中国）有限公司

## 商标

- 「麦当劳」「McDonald's」及相关品牌、商品名称、商品图片的商标与版权归相应权利人所有
- 本项目仅在比赛说明、MCP 集成说明与真实返回摘要中作必要引用；作者的 MIT 授权范围聚焦其原创贡献

## 数据与工具契约

- 菜单、价格、门店、优惠与订单相关事实均以麦当劳官方 MCP（`https://mcp.mcd.cn`）的当次返回为准，公开说明标注查询范围与时间
- `.codebuddy/skills/manmandian/references/mcd-tool-contracts.json`：由 2026-10-10 WorkBuddy 注入的 `mcd-mcp` 工具定义派生，仅保留名称、脱敏输入契约、分类与校验哈希；原始导出由作者在本机受保护环境保管
- `docs/EVIDENCE_LEDGER.jsonl`：公开台账采用最小披露，精确账户数据与个人信息留在作者本机原始记录

## 项目视觉资产

以下 PNG 均于 2026-10-09 使用 OpenAI 内置图像生成工具为本项目创作。角色和场景采用虚构概念插画，菜单语义聚焦汉堡、鸡肉汉堡、薯条、麦乐鸡与饮料：

- `assets/manmandian-hero-16x9.png`：项目主视觉
- `assets/manmandian-story-4-panels.png`：四格自主点餐故事
- `assets/manmandian-accessible-ways.png`：简笔水彩式多入口场景
- `assets/manmandian-co-design.png`：顾客、员工与产品团队平等共创场景

以下 SVG 由项目内确定性绘制，采用系统字体回退：

- `assets/manmandian-three-steps.svg`
- `assets/manmandian-eight-guardrails.svg`
- `assets/manmandian-status-board.svg`
- `assets/manmandian-poems.svg`
- `assets/manmandian-mcp-35-map.svg`

全部视觉资产采用通用包装、虚构人物与概念场景；项目身份始终表述为独立参赛作品。README 为每张图提供替代文字，并为关键信息图提供可展开的纯文字版本。未来使用官方商品图片、门店照片或真实人物素材时，先取得对应授权并在本文件登记。
