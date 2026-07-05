"""KOL radar Streamlit panel for the local workstation."""

from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st

from tradingagents.dataflows.kol.importers import load_jsonl
from tradingagents.dataflows.kol.obsidian_sync import ObsidianSync
from tradingagents.dataflows.kol.service import KolRadarService, RISK_DISCLOSURE
from tradingagents.dataflows.kol.storage import KolStorage


LOCAL_KOL_DB_PATH = Path(r"C:\Users\35230\.tradingagents\kol\local_kol_radar.sqlite")


def kol_db_path() -> Path:
    return Path(os.environ.get("TRADINGAGENTS_KOL_DB_PATH") or LOCAL_KOL_DB_PATH).expanduser()


def get_kol_counts(db_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(db_path or kol_db_path())
    if not path.exists():
        return {"db_path": str(path), "exists": False, "raw_posts": 0, "signals": 0, "authors": 0}

    storage = KolStorage(path)
    with storage.connect() as conn:
        raw_posts = conn.execute("SELECT COUNT(*) AS count FROM raw_kol_posts").fetchone()["count"]
        signals = conn.execute("SELECT COUNT(*) AS count FROM kol_signals").fetchone()["count"]
        authors = conn.execute("SELECT COUNT(*) AS count FROM author_scores").fetchone()["count"]
    return {
        "db_path": str(path),
        "exists": True,
        "raw_posts": int(raw_posts),
        "signals": int(signals),
        "authors": int(authors),
    }


def recent_signal_rows(limit: int = 50, db_path: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(db_path or kol_db_path())
    if not path.exists():
        return []

    storage = KolStorage(path)
    rows = []
    for signal in storage.list_signals()[:limit]:
        rows.append(
            {
                "时间": signal.published_at.strftime("%Y-%m-%d %H:%M"),
                "股票": signal.symbol,
                "名称": signal.stock_name,
                "动作": signal.action,
                "周期": signal.horizon,
                "作者": signal.author_id,
                "置信度": round(signal.llm_confidence, 2),
                "发布价": signal.price_at_post if signal.price_at_post is not None else "缺失",
                "来源": signal.source_url,
            }
        )
    return rows


def render_kol_status_badge() -> None:
    counts = get_kol_counts()
    if counts["exists"]:
        st.caption(f"KOL DB: {counts['signals']} 条信号 / {counts['raw_posts']} 条原帖")
    else:
        st.caption("KOL DB: 未创建")


def render_kol_radar_panel(default_symbol: str = "", default_trade_date: date | None = None) -> None:
    st.markdown("### KOL 信息雷达")
    st.caption(RISK_DISCLOSURE)

    counts = get_kol_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("原始帖子", counts["raw_posts"])
    c2.metric("确认信号", counts["signals"])
    c3.metric("作者评分", counts["authors"])
    c4.metric("数据库", "就绪" if counts["exists"] else "未创建")

    service = KolRadarService(db_path=kol_db_path())
    trade_date = default_trade_date or date.today()

    st.markdown("#### 热点概览")
    hot_col, sync_col = st.columns([3, 1])
    with hot_col:
        lookback_date = st.date_input("热点日期", value=trade_date, key="kol_hotspot_date")
    with sync_col:
        st.write("")
        st.write("")
        if st.button("同步 Obsidian", use_container_width=True):
            ObsidianSync(service.storage).sync_full()
            st.success("已同步到 Obsidian KOL-Radar")

    st.markdown(service.get_kol_hotspots(lookback_date, top_n=10))

    st.markdown("#### 最近信号")
    rows = recent_signal_rows()
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("暂无 KOL 信号。可以先导入 JSONL 样例或运行本机烟测脚本。")

    st.markdown("#### 个股摘要")
    q1, q2, q3 = st.columns([2, 1, 1])
    symbol = q1.text_input("股票代码", value=default_symbol, placeholder="例如 300750", key="kol_symbol")
    summary_date = q2.date_input("交易日", value=trade_date, key="kol_summary_date")
    lookback_days = q3.number_input("回看天数", min_value=1, max_value=60, value=7, step=1, key="kol_lookback")
    if symbol:
        st.markdown(service.get_kol_summary(symbol.strip(), summary_date, int(lookback_days)))

    st.markdown("#### 作者评分")
    author = st.text_input("作者 ID", placeholder="例如 local_teacher_a", key="kol_author")
    if author:
        st.markdown(service.get_author_score(author.strip()))

    st.markdown("#### 导入 JSONL")
    uploaded = st.file_uploader("选择 KOL JSONL 文件", type=["jsonl"], key="kol_jsonl_upload")
    if uploaded and st.button("导入并解析", type="primary", use_container_width=True):
        with tempfile.NamedTemporaryFile("wb", suffix=".jsonl", delete=False) as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = Path(tmp.name)
        try:
            posts = load_jsonl(tmp_path)
            signal_count = service.ingest_raw_posts(posts)
            st.success(f"已导入 {len(posts)} 条帖子，生成 {signal_count} 条确认信号。")
        finally:
            tmp_path.unlink(missing_ok=True)
