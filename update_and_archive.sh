#!/bin/bash
set -e

echo "==================================================="
echo "[START] Starting rolling release automation..."
echo "==================================================="

# Pre-check: Ensure at least one application package file exists
shopt -s nullglob
files=(*.apk *.apkm *.xapk *.apks *.zip)
if [ ${#files[@]} -eq 0 ]; then
    echo "[ERROR] No package files (*.apk, *.apkm, *.xapk, *.apks, *.zip) found to upload!"
    exit 1
fi

echo "[INFO] Found ${#files[@]} package file(s) ready for release:"
for f in "${files[@]}"; do
    echo "  - $f ($(du -h "$f" | cut -f1))"
done

# Step 1: Delete the old "previous" release to make room
echo "[INFO] Cleaning up older versions..."
gh release delete previous --repo "$REPO" --cleanup-tag -y 2>/dev/null || true 

# Step 2: Rename the current 'latest' release to 'previous'
echo "[INFO] Archiving current 'latest' release to 'previous'..."
gh release edit latest --tag previous --title "Previous APK Builds" --repo "$REPO" 2>/dev/null || true

# Step 3: Create a brand new, empty 'latest' release
echo "[INFO] Creating new 'latest' release..."
git push --delete origin latest 2>/dev/null || true 
gh release create latest --repo "$REPO" --title "Latest APK Builds" --notes "Automated update"

# Step 4: Loop through and upload all package files
echo "[INFO] Scanning and uploading application files..."
for f in "${files[@]}"; do
    echo "  [+] Uploading: $f"
    gh release upload latest "$f" --repo "$REPO" --clobber
done

echo "==================================================="
echo "[SUCCESS] 'latest' updated. Old version preserved under 'previous'."
echo "==================================================="
