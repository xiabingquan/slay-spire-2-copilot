#!/usr/bin/env python3
"""spirectl entry point — thin shim over the spirectl_lib package.

Invocation stays `python3 bridge/spirectl.py <subcommand>`; all logic lives
in bridge/spirectl_lib/ and this file only parses nothing and delegates.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spirectl_lib.cli import main

if __name__ == "__main__":
    sys.exit(main())
