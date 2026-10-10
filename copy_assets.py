import os
import shutil
from pathlib import Path

source_dir = Path(os.environ.get("ASSET_SOURCE_DIR", ""))
target_dir = Path(__file__).resolve().parent / "static" / "images"

if not source_dir.is_dir():
    raise SystemExit("Set ASSET_SOURCE_DIR to the directory containing generated image assets.")

target_dir.mkdir(parents=True, exist_ok=True)

for pattern, filename in (("*_hero_*.png", "hero.png"), ("control_panel_preview_*.png", "panel.png")):
    for asset in source_dir.glob(pattern):
        shutil.copy(asset, target_dir / filename)
        print(f"Copied {asset.name} -> static/images/{filename}")
