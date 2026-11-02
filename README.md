# apk-vanced

Automated rolling release workflow for Android packages (`.apk`, `.apkm`, `.xapk`, `.apks`, `.zip`) triggered via GitHub Actions using direct download URLs.

## Features

- **Direct Download via GitHub Actions**: Trigger downloads by providing direct URLs directly in the Actions UI.
- **Flexible Delimiters**: Enter multiple URLs on a single line separated by **spaces**, **commas** (`,`), **semicolons** (`;`), or pasted **newlines**.
- **Custom Output Names**: Optionally specify a custom filename immediately after any URL.
- **Zero Scraper Dependencies**: No Google Play tokens, keystores, Python dependencies, or scraper tools required.
- **Automated Rolling Releases**: Automatically maintains `latest` and `previous` GitHub releases via `update_and_archive.sh`.

---

## How to Use

1. Navigate to the **Actions** tab in your repository.
2. Select the **Direct Download & Rolling Release** workflow from the left sidebar.
3. Click **Run workflow**.
4. In the **Direct download URLs** input field, enter your URLs.

> [!NOTE]
> GitHub Actions displays manual inputs as single-line text boxes, so pressing `Enter` to create a new line is disabled by GitHub's web interface. You can separate multiple URLs directly on the single line using **spaces**, **commas**, or **semicolons** (or by pasting a multi-line list copied from your clipboard).

### Input Format Examples:

#### 1. Space-separated URLs (Single Line)
```text
https://example.com/app1.apk https://example.com/app2.apkm https://example.com/app3.zip
```

#### 2. Comma or Semicolon Separated
```text
https://example.com/app1.apk, https://example.com/app2.apkm; https://example.com/app3.zip
```

#### 3. With Custom Filenames
Place the desired filename right after the URL:
```text
https://example.com/dl?id=123 app1.apk https://example.com/dl?id=456 app2.apkm
```

#### 4. Pasted Multi-line List
You can also copy a multi-line list from a text editor and paste it directly into the input:
```text
https://example.com/app1.apk
https://example.com/app2.apkm custom_app2.apkm
```

---

## Release Process

When the workflow runs:
1. Each provided URL is downloaded with `curl` (using redirects, retry logic, and browser `User-Agent`).
2. Filenames are automatically resolved from the server's `Content-Disposition` header / URL path, or from the custom name if provided.
3. [`update_and_archive.sh`](update_and_archive.sh) executes:
   - Validates that at least one package file (`*.apk`, `*.apkm`, `*.xapk`, `*.apks`, `*.zip`) was downloaded.
   - Archives the existing `latest` release to `previous`.
   - Creates a fresh `latest` release.
   - Uploads all downloaded packages to the new `latest` release.
