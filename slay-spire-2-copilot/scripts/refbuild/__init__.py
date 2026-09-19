"""refbuild — spirectl_lib/data JSON store build, curation overlays, and check."""
import sys
from pathlib import Path

# bridge/ must be importable: spirectl_lib.schema is the single schema source
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "bridge"))
