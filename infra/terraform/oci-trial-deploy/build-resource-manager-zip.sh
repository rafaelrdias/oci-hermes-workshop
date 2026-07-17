#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$ROOT_DIR/dist"
ZIP_NAME="oci-hermes-resource-manager.zip"
ZIP_PATH="$DIST_DIR/$ZIP_NAME"

mkdir -p "$DIST_DIR"

python3 - "$ROOT_DIR" "$ZIP_PATH" <<'PY'
import os
import sys
import zipfile
from pathlib import Path

root = Path(sys.argv[1]).resolve()
zip_path = Path(sys.argv[2]).resolve()
excluded_dirs = {".terraform", "dist"}
excluded_names = {
    "terraform.tfvars",
    "crash.log",
    ".DS_Store",
}
excluded_suffixes = (
    ".tfstate",
    ".tfplan",
)

with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith("._")]
        for name in files:
            if name.startswith("._"):
                continue
            if name in excluded_names:
                continue
            if name.startswith("crash.") and name.endswith(".log"):
                continue
            if name.endswith(excluded_suffixes) or ".tfstate." in name:
                continue
            path = Path(current) / name
            if path.resolve() == zip_path:
                continue
            archive.write(path, path.relative_to(root).as_posix())
PY

echo "$ZIP_PATH"
