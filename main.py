"""Entry point principal do projeto."""

import sys
from pathlib import Path

src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from judo_data.pipeline import main

if __name__ == "__main__":
    main()
