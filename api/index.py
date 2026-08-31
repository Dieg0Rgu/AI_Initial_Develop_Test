import sys
import os
from pathlib import Path

# Add project root and backend to python path for Vercel Serverless Functions
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"

for p in [str(root_dir), str(backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.main import app  # noqa: F401, E402
except ImportError:
    from backend.app.main import app  # noqa: F401, E402
