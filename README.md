# apk-vanced

Automated rolling release downloader for Android application packages (APK and APKM) directly from Google Play Store using [alltechdev/gplay-apk-downloader](https://github.com/alltechdev/gplay-apk-downloader).

## Features
- **Direct Google Play Downloads**: Downloads apps using official package IDs without scraping APKMirror.
- **APKM Bundle Packaging**: Wraps split APKs into `.apkm` zip bundles with **original Google Play signatures preserved**, ready for processing by `APKEditor` or ReVanced.
- **Standalone APK Support**: Automatically preserves and outputs standalone `.apk` for apps without splits (or merged `.apk` if requested).
- **Automated Rolling Releases**: Maintains `latest` and `previous` GitHub releases automatically.

---

## Configuration (`apps.json`)

Apps to download are specified in `apps.json`:

```json
{
  "options": {
    "outDir": "downloads"
  },
  "apps": [
    {
      "package": "com.google.android.youtube",
      "arch": "arm64",
      "format": "apkm",
      "output_name": "com.google.android.apps.youtube-latest-arm64.apkm"
    },
    {
      "package": "com.arlosoft.macrodroid",
      "arch": "arm64",
      "format": "apk",
      "output_name": "com.arlosoft.macrodroid-latest-all.apk"
    }
  ]
}
```

### Options:
- `package`: The Google Play application ID (e.g. `com.google.android.youtube`).
- `arch`: Target CPU architecture (`arm64` or `armv7`, default: `arm64`).
- `format`: 
  - `"apkm"`: If the app has splits, bundles them into an `.apkm` archive with original signatures intact. If the app is standalone, saves as `.apk`.
  - `"apk"`: Merges splits into a single `.apk` using APKEditor and signs with debug key.
- `output_name`: Desired output filename.

---

## Authentication Setup (GitHub Actions Secrets)

Google Play Store downloads require authentication. Configure the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions**):

| Secret | Description |
|---|---|
| `GPLAY_EMAIL` | Your Google account email (recommended: burner/throwaway account) |
| `GPLAY_AAS_TOKEN` | Long-lived AAS token for Google Play authentication |

### How to generate an AAS token:
1. Clone `alltechdev/gplay-apk-downloader`:
   ```bash
   git clone --depth 1 https://github.com/alltechdev/gplay-apk-downloader.git
   cd gplay-apk-downloader
   pip install -r requirements.txt
   ```
2. Run browser login on your local machine:
   ```bash
   python3 gplay-downloader.py auth-account --browser
   ```
3. Sign into your Google account in the browser window.
4. Copy the `aasToken` value stored in `~/.gplay-auth.json` and set it as `GPLAY_AAS_TOKEN` in GitHub Secrets.

---

## Merging `.apkm` Files Later with APKEditor

To merge any `.apkm` bundle into a single standalone `.apk` locally:

```bash
java -jar APKEditor.jar m -i com.google.android.apps.youtube-latest-arm64.apkm -o youtube-merged.apk
```