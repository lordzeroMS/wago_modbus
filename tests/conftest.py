from __future__ import annotations

import sys
from pathlib import Path

CUSTOM_COMPONENTS = Path(__file__).resolve().parents[1] / "custom_components"
sys.path.insert(0, str(CUSTOM_COMPONENTS))
