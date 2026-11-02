# apk-vanced

Automated rolling release workflow for Android packages (`.apk`, `.apkm`, `.xapk`, `.apks`, `.zip`) triggered via GitHub Actions using direct download URLs.

## Features

- **Direct Download via GitHub Actions**: Trigger downloads by providing direct URLs directly in the Actions UI.
- **Custom Output Names**: Optionally specify a custom filename per download link.
- **No Dependencies or Tokens**: Zero external scraper dependencies, Google tokens, or keystores required.
- **Automated Rolling Releases**: Maintains `latest` and `previous` GitHub releases automatically using `update_and_archive.sh`.

---

## How to Use

1. Navigate to the **Actions** tab in your repository.
2. Select the **Direct Download & Rolling Release** workflow from the left sidebar.
3. Click **Run workflow**.
4. In the **Direct download URLs** input box, enter your URLs (one per line).

### Input Format Examples:

```text
# Direct download (filename auto-inferred from server / headers)
https://example.com/downloads/com.google.android.youtube-arm64.apkm

# Direct download with custom filename
https://example.com/dl?id=12345 com.reddit.frontpage.apk

# Multiple links can be specified
https://example.com/app1.apk
https://example.com/app2.apkm app2-arm64.apkm
```

- Blank lines and lines starting with `#` are automatically ignored.
- If a custom filename is provided after a space, the file is saved with that name.
- Otherwise, `curl` extracts the filename from the server's `Content-Disposition` header or the URL.

---

## Release Process

When the workflow runs:
1. All files from the provided URLs are downloaded.
2. [`update_and_archive.sh`](update_and_archive.sh) executes:
   - Deletes any older `previous` release.
   - Renames the existing `latest` release tag and title to `previous`.
   - Creates a fresh `latest` release.
   - Uploads all downloaded packages (`*.apk`, `*.apkm`, `*.xapk`, `*.apks`, `*.zip`) to the new `latest` release.
