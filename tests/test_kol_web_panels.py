from datetime import datetime, timezone

from tradingagents.dataflows.kol.models import RawKolPost
from tradingagents.dataflows.kol.service import KolRadarService
from web.components.kol_radar_panel import get_kol_counts, recent_signal_rows
from web.components.local_system_panel import horizon_kol_status, obsidian_moc_uri


def test_kol_panel_counts_empty_missing_db(tmp_path):
    missing = tmp_path / "missing.sqlite"

    counts = get_kol_counts(missing)

    assert counts["exists"] is False
    assert counts["signals"] == 0
    assert counts["raw_posts"] == 0


def test_kol_panel_reads_recent_signals(tmp_path):
    db_path = tmp_path / "kol.sqlite"
    service = KolRadarService(db_path=db_path)
    post = RawKolPost(
        post_id="p1",
        author_id="local_teacher_a",
        platform="douyin",
        published_at=datetime(2026, 7, 5, 9, 30, tzinfo=timezone.utc),
        content="低吸 300750 宁德时代，短线观察。",
        source_url="https://www.douyin.com/video/1",
        content_hash="hash",
    )
    service.ingest_raw_posts([post], stock_name_map={"300750": "宁德时代"})

    counts = get_kol_counts(db_path)
    rows = recent_signal_rows(db_path=db_path)

    assert counts["exists"] is True
    assert counts["signals"] == 1
    assert rows[0]["股票"] == "300750"
    assert rows[0]["作者"] == "local_teacher_a"


def test_obsidian_moc_uri_uses_kol_radar_moc(monkeypatch, tmp_path):
    vault = tmp_path / "My Vault"
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(vault))

    uri = obsidian_moc_uri()

    assert uri.startswith("obsidian://open?")
    assert "vault=My%20Vault" in uri
    assert "KOL-Radar" in uri


def test_horizon_kol_status_reads_enabled_config(tmp_path):
    root = tmp_path / "Horizon"
    config = root / "data" / "config.json"
    config.parent.mkdir(parents=True)
    config.write_text(
        """
{
  "sources": {
    "kol": {
      "enabled": true,
      "db_path": "C:/Users/35230/.tradingagents/kol/local_kol_radar.sqlite",
      "lookback_hours": 168
    }
  }
}
""",
        encoding="utf-8",
    )

    status = horizon_kol_status(root)

    assert status["exists"] is True
    assert status["enabled"] is True
    assert status["lookback_hours"] == 168
