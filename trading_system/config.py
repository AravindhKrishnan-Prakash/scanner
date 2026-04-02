import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class WatchlistItem:
    query: str
    label: Optional[str] = None


@dataclass
class UserProfile:
    capital: float = 100000.0
    risk_per_trade_pct: float = 1.0
    risk_level: str = "low"
    use_leverage: bool = False
    leverage_multiplier: float = 5.0  # MIS margin typically 5x-20x


@dataclass
class ScannerSettings:
    poll_seconds: int = 30
    history_days: int = 120
    support_resistance_lookback: int = 20
    minimum_adx: float = 18.0
    minimum_volume_ratio: float = 1.05
    trading_mode: str = "swing"  # "swing" or "intraday"
    intraday_candle_interval: str = "30minute"  # "1minute" or "30minute" (Upstox limitation)
    intraday_exit_time: str = "15:15"  # Square off time


@dataclass
class RuntimeConfig:
    market_index_query: str = "NIFTY 50"
    watchlist: List[WatchlistItem] = field(default_factory=list)
    user_profile: UserProfile = field(default_factory=UserProfile)
    scanner: ScannerSettings = field(default_factory=ScannerSettings)


def load_env_file(path: str | Path = ".env") -> Dict[str, str]:
    env_path = Path(path)
    parsed: Dict[str, str] = {}

    if not env_path.exists():
        return parsed

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
        parsed[key] = value

    return parsed


def load_runtime_config(path: str | Path = "config/watchlist.json") -> RuntimeConfig:
    config_path = Path(path)
    raw = json.loads(config_path.read_text(encoding="utf-8"))

    watchlist = [
        WatchlistItem(query=str(item["query"]).strip(), label=item.get("label"))
        for item in raw.get("watchlist", [])
        if str(item.get("query", "")).strip()
    ]

    user_profile_raw = raw.get("user_profile", {})
    scanner_raw = raw.get("scanner", {})

    return RuntimeConfig(
        market_index_query=str(raw.get("market_index_query", "NIFTY 50")).strip(),
        watchlist=watchlist,
        user_profile=UserProfile(
            capital=float(user_profile_raw.get("capital", 100000.0)),
            risk_per_trade_pct=float(user_profile_raw.get("risk_per_trade_pct", 1.0)),
            risk_level=str(user_profile_raw.get("risk_level", "low")).strip().lower(),
            use_leverage=bool(user_profile_raw.get("use_leverage", False)),
            leverage_multiplier=float(user_profile_raw.get("leverage_multiplier", 5.0)),
        ),
        scanner=ScannerSettings(
            poll_seconds=int(scanner_raw.get("poll_seconds", 30)),
            history_days=int(scanner_raw.get("history_days", 120)),
            support_resistance_lookback=int(scanner_raw.get("support_resistance_lookback", 20)),
            minimum_adx=float(scanner_raw.get("minimum_adx", 18.0)),
            minimum_volume_ratio=float(scanner_raw.get("minimum_volume_ratio", 1.05)),
            trading_mode=str(scanner_raw.get("trading_mode", "swing")).strip().lower(),
            intraday_candle_interval=str(scanner_raw.get("intraday_candle_interval", "30minute")).strip(),
            intraday_exit_time=str(scanner_raw.get("intraday_exit_time", "15:15")).strip(),
        ),
    )
