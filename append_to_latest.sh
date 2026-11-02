#!/bin/bash
set -e

echo "==================================================="
echo "[START] Appending files to 'latest' release..."
echo "==================================================="

# Step 0: Auto-rename packages based on apps.json mapping rules if available
if [ -f "rename_apps.py" ] && command -v python3 &>/dev/null; then
    python3 rename_apps.py
fi

# Pre-check: Ensure at least one application package file exists
shopt -s nullglob
files=(*.apk *.apkm *.xapk *.apks *.zip)
if [ ${#files[@]} -eq 0 ]; then
    echo "[ERROR] No package files (*.apk, *.apkm, *.xapk, *.apks, *.zip) found to upload!"
    exit 1
fi

echo "[INFO] Found ${#files[@]} package file(s) ready to upload:"
for f in "${files[@]}"; do
    echo "  - $f ($(du -h "$f" | cut -f1))"
done

# Step 1: Ensure 'latest' release exists; create it if it doesn't
if ! gh release view latest --repo "$REPO" >/dev/null 2>&1; then
    echo "[INFO] 'latest' release does not exist. Creating new 'latest' release..."
    gh release create latest --repo "$REPO" --title "Latest APK Builds" --notes "Automated update"
fi

# Step 2: Upload new files to existing 'latest' release
echo "[INFO] Appending files to existing 'latest' release..."
for f in "${files[@]}"; do
    echo "  [+] Uploading: $f"
    gh release upload latest "$f" --repo "$REPO" --clobber
done

echo "==================================================="
echo "[SUCCESS] Successfully added files to 'latest' release without modifying existing files."
echo "==================================================="
