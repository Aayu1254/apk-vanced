#!/bin/bash

echo "==================================================="
echo "[START] Starting rolling release automation..."
echo "==================================================="

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

# Step 4: Loop through and upload all .apk and .apkm files
echo "[INFO] Scanning and uploading application files..."
shopt -s nullglob 
for f in *.apk *.apkm; do
    echo "  [+] Uploading: $f"
    gh release upload latest "$f" --repo "$REPO" --clobber
done

echo "==================================================="
echo "[SUCCESS] 'latest' updated. Old version preserved under 'previous'."
echo "==================================================="