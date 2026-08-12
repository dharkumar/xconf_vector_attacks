"""
Pytest puts this file's own directory (tests/) on sys.path, not
flagship-showcase/ itself -- so `import adapters` etc. would fail without
this. Inserted once, here, rather than repeated per test file.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
