# apk-vanced

Automated release workflow for Android packages (`.apk`, `.apkm`, `.xapk`, `.apks`, `.zip`) triggered via GitHub Actions using direct download URLs.

## Features

- **Direct Download via GitHub Actions**: Trigger downloads by providing direct URLs directly in the Actions UI.
- **Automatic Filename Analysis & Renaming**: Automatically detects package IDs or keywords in downloaded filenames and assigns standardized names defined in `apps.json`.
- **Flexible Delimiters**: Enter multiple URLs on a single line separated by **spaces**, **commas** (`,`), **semicolons** (`;`), or pasted **newlines**.
- **Custom Output Names**: Optionally specify a custom filename immediately after any URL.
- **Two Workflow Modes**:
  - **Rolling Release**: Archives the current `latest` release to `previous` and creates a fresh `latest` release.
  - **Append to Latest**: Uploads new files directly to the existing `latest` release without removing or altering existing files.
- **Zero Scraper Dependencies**: No Google Play tokens, keystores, or scraper tools required.

---

## Automatic Name Mapping (`apps.json`)

If `apps.json` is present in the repository, downloaded files are automatically analyzed and renamed before upload.

Example `apps.json`:

```json
{
  "apps": [
    {
      "package": "com.google.android.youtube",
      "output_name": "com.google.android.youtube-latest-arm64-v8a.apkm"
    },
    {
      "package": "com.google.android.apps.youtube.music",
      "output_name": "com.google.android.apps.youtube.music-latest-arm64-v8a.apkm"
    },
    {
      "package": "com.reddit.frontpage",
      "output_name": "com.reddit.frontpage-latest-arm64-v8a.apkm"
    },
    {
      "package": "ch.protonvpn.android",
      "output_name": "ch.protonvpn.android-latest-arm64-v8a.apkm"
    }
  ]
}
```

- **Smart Extension Harmonization**: If the downloaded file is a standalone `.apk` but `output_name` specifies `.apkm`, it automatically adjusts the extension to `.apk`.
- **Variant Matching**: Matches `com.package.name`, `com_package_name`, and `com-package-name` anywhere in the filename.

---

## Available Workflows

### 1. Direct Download & Rolling Release (`apk-get.yml`)
Use this workflow when you want to start a new batch of builds:
- Archives the existing `latest` release to `previous`.
- Creates a clean `latest` release with only the newly downloaded files.

### 2. Append to Latest Release (`apk-append.yml`)
Use this workflow when you want to add more files to your current `latest` release:
- Keeps all existing files in `latest` intact.
- Uploads the new files directly alongside the existing ones.

---

## How to Use

1. Navigate to the **Actions** tab in your repository.
2. Select either **Direct Download & Rolling Release** or **Append to Latest Release** from the left sidebar.
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

#### 3. With Explicit Custom Filename (Overrides `apps.json`)
Place the desired filename right after the URL:
```text
https://example.com/dl?id=123 myapp.apk https://example.com/dl?id=456 custom.apkm
```

#### 4. Pasted Multi-line List
You can also copy a multi-line list from a text editor and paste it directly into the input:
```text
https://example.com/com.reddit.frontpage_v2026.apk
https://example.com/youtube_bundle.apkm
```
