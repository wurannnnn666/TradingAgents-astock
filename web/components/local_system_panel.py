"""Local workstation status panel for the KOL radar setup."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote

import streamlit as st

from web.components.kol_radar_panel import get_kol_counts, kol_db_path


DEFAULT_OBSIDIAN_VAULT = Path(r"C:\Users\35230\Documents\Obsidian Vault")
DEFAULT_HORIZON_ROOT = Path(r"C:\Users\35230\Documents\obsidian\Horizon")


def obsidian_vault_path() -> Path:
    return Path(os.environ.get("OBSIDIAN_VAULT_PATH") or DEFAULT_OBSIDIAN_VAULT).expanduser()


def obsidian_moc_uri() -> str:
    vault_name = obsidian_vault_path().name
    return f"obsidian://open?vault={quote(vault_name)}&file={quote('KOL-Radar/_MOC.md')}"


def horizon_kol_status(horizon_root: str | Path = DEFAULT_HORIZON_ROOT) -> dict[str, Any]:
    root = Path(horizon_root)
    config_path = root / "data" / "config.json"
    if not config_path.exists():
        return {"exists": False, "enabled": False, "config_path": str(config_path), "db_path": ""}

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "exists": True,
            "enabled": False,
            "config_path": str(config_path),
            "db_path": "",
            "error": str(exc),
        }

    kol = (data.get("sources") or {}).get("kol") or {}
    return {
        "exists": True,
        "enabled": bool(kol.get("enabled")),
        "config_path": str(config_path),
        "db_path": str(kol.get("db_path") or ""),
        "lookback_hours": kol.get("lookback_hours"),
    }


def render_local_system_panel() -> None:
    st.markdown("### 本机系统")
    st.caption("本页只显示本机路径和启用状态，不展示 .env、Cookie 或 API Key。")

    counts = get_kol_counts()
    db = kol_db_path()
    vault = obsidian_vault_path()
    moc = vault / "KOL-Radar" / "_MOC.md"
    horizon = horizon_kol_status()

    c1, c2, c3 = st.columns(3)
    c1.metric("KOL SQLite", "存在" if counts["exists"] else "未创建")
    c2.metric("Obsidian 投影", "存在" if moc.exists() else "未生成")
    c3.metric("Horizon KOL", "启用" if horizon["enabled"] else "未启用")

    st.markdown("#### 本机路径")
    st.code(
        "\n".join(
            [
                f"TRADINGAGENTS_KOL_DB_PATH={db}",
                f"OBSIDIAN_VAULT_PATH={vault}",
                f"HORIZON_CONFIG={horizon['config_path']}",
            ]
        ),
        language="text",
    )

    st.markdown("#### 快速打开")
    st.link_button("打开 Obsidian KOL Radar", obsidian_moc_uri(), use_container_width=True)
    st.link_button("打开本机 UI", "http://localhost:8501", use_container_width=True)

    st.markdown("#### Horizon 状态")
    if horizon.get("error"):
        st.error(f"Horizon config 解析失败: {horizon['error']}")
    elif horizon["exists"]:
        st.json(
            {
                "enabled": horizon["enabled"],
                "db_path": horizon["db_path"],
                "lookback_hours": horizon["lookback_hours"],
            }
        )
    else:
        st.info("未找到 Horizon data/config.json。")

    st.markdown("#### 本机烟测")
    st.code(
        "\n".join(
            [
                r"powershell -ExecutionPolicy Bypass -File scripts\run-local-kol-smoke.ps1",
                r"powershell -ExecutionPolicy Bypass -File scripts\start-local-kol-ui.ps1",
            ]
        ),
        language="powershell",
    )
