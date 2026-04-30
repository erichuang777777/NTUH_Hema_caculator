from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.ntuh_price_updater.cli import main


def with_repo_defaults(argv: list[str]) -> list[str]:
    args = list(argv)
    if "--data" not in args:
        args.extend(["--data", str(ROOT / "data" / "heme_drugs_clean.json")])
    return args


if __name__ == "__main__":
    raise SystemExit(main(with_repo_defaults(sys.argv[1:])))
