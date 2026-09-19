"""Paths and domain lists for the spirectl_lib/data JSON store."""
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_LIVE_IDS = SKILL_ROOT / "scripts" / ".cache" / "live_ids.json"
DEFAULT_OUT_DIR = SKILL_ROOT / "bridge" / "spirectl_lib" / "data"
CODEX_CACHE = SKILL_ROOT / "scripts" / ".cache" / "codex"

DOMAINS = [
    "characters", "cards", "powers", "relics", "potions",
    "afflictions", "intents", "monsters", "events",
]

# Live-id census buckets that --check treats as hard coverage requirements vs
# report-only soft buckets (see census.run_check).
HARD_CENSUS_DOMAINS = [
    "move_ids", "power_ids", "relic_ids", "card_ids", "potion_ids",
    "event_option_ids", "card_option_ids", "character_ids",
    "intent_classes", "intent_types", "event_ids",
]
SOFT_CENSUS_DOMAINS = ["creature_names", "relic_option_ids"]
