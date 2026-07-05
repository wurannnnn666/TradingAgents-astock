# 本机 KOL 雷达系统二开总结

## 总览

本分支把 KOL 信息雷达接入 TradingAgents-Astock 本机工作流，并与 Horizon、Obsidian 形成闭环。系统定位是研究辅助，不自动荐股、不下单。

## 已完成内容

- 新增 KOL 数据闭环：JSONL/抖音适配、SQLite 存储、信号抽取、作者评分、Obsidian 投影、Horizon source 输出。
- 接入 TradingAgents social analyst：提供 `get_kol_summary`、`get_kol_hotspots`、`get_author_score`，让个股分析能读取 KOL 雷达摘要。
- 接入 Horizon：新增 `kol` source，可从 TradingAgents KOL SQLite 输出 `ContentItem`。
- 新增本机 Streamlit 总控台：`个股分析`、`KOL 雷达`、`本机系统` 三个页签集中展示。
- 新增 Obsidian 出口：默认同步到 `C:\Users\35230\Documents\Obsidian Vault\KOL-Radar`。
- 新增本机启动脚本：`scripts/start-local-kol-ui.ps1`，固定打开 `http://localhost:8501`，并允许局域网访问。
- 新增本机烟测脚本：`scripts/run-local-kol-smoke.ps1`，可把样例 KOL 帖子导入 SQLite 并同步 Obsidian。
- 更新工程协作配置：Agent skills issue tracker 指向 `wurannnnn666/TradingAgents-astock`。

## 打开方式

本机 UI：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start-local-kol-ui.ps1
```

浏览器入口：

- 本机：`http://localhost:8501`
- 局域网：启动脚本会显示当前机器的 LAN URL，例如 `http://172.27.201.122:8501`

如果局域网设备无法访问，需要用管理员 PowerShell 放开端口：

```powershell
New-NetFirewallRule -DisplayName "TradingAgents Local KOL UI" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8501 -Profile Private
```

## GitHub 分支

- TradingAgents-Astock 主功能分支：`codex/kol-radar`
- TradingAgents-Astock 本机系统分支：`codex/local-kol-system`
- Horizon 主功能分支：`codex/kol-radar`
- Horizon 本机系统分支：`codex/local-kol-system`

Fork 地址：

- `https://github.com/wurannnnn666/TradingAgents-astock`
- `https://github.com/wurannnnn666/Horizon`

## 验证记录

- TradingAgents KOL/Web 测试：`12 passed`
- Horizon KOL source 测试：`6 passed`
- Streamlit 本机启动检查：`HTTP 200`
- Streamlit 监听地址：`0.0.0.0:8501`

## 重要约束

- SQLite 是 KOL 数据真相源。
- Obsidian 只作为可重建投影。
- UI 不展示 `.env`、Cookie、API Key。
- KOL 输出始终保留“仅供研究，不构成投资建议”风险声明。
