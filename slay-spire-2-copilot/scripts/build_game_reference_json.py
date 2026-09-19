#!/usr/bin/env python3
"""Build references/game JSON DB — thin entry over the refbuild package.

Usage (unchanged):
  python3 scripts/build_game_reference_json.py            # overlay refresh + write
  python3 scripts/build_game_reference_json.py --check    # coverage gate
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from refbuild.build import main

if __name__ == "__main__":
    sys.exit(main())
