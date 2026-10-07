#!/usr/bin/env python3
"""
Orchestrator script to download Android apps using alltechdev/gplay-apk-downloader.
Supports:
- Google Account authentication using AAS token (GPLAY_EMAIL, GPLAY_AAS_TOKEN)
- Dispenser URL authentication (DISPENSER_URL)
- APKM bundling for split APKs (preserving original signatures for APKEditor)
- Standalone APK downloads
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run_cmd(cmd, cwd=None, env=None, check=True):
    print(f"[CMD] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")
    return result.returncode


def authenticate(tool_dir):
    """Authenticate using AAS token or token dispenser."""
    gplay_script = tool_dir / "gplay-downloader.py"
    if not gplay_script.exists():
        raise FileNotFoundError(f"gplay-downloader.py not found at {gplay_script}")

    email = os.environ.get("GPLAY_EMAIL", "").strip()
    aas_token = os.environ.get("GPLAY_AAS_TOKEN", "").strip()
    oauth_token = os.environ.get("GPLAY_OAUTH_TOKEN", "").strip()
    dispenser_url = os.environ.get("DISPENSER_URL", "").strip()

    if email and aas_token:
        print(f"[AUTH] Authenticating with personal Google account ({email}) via AAS token...")
        run_cmd([
            sys.executable,
            str(gplay_script),
            "auth-account",
            "--email", email,
            "--aas-token", aas_token,
        ], cwd=tool_dir)
        return True

    if email and oauth_token:
        print(f"[AUTH] Authenticating with personal Google account ({email}) via OAuth token...")
        run_cmd([
            sys.executable,
            str(gplay_script),
            "auth-account",
            "--email", email,
            "--oauth-token", oauth_token,
        ], cwd=tool_dir)
        return True

    if dispenser_url:
        print(f"[AUTH] Authenticating via token dispenser: {dispenser_url}...")
        run_cmd([
            sys.executable,
            str(gplay_script),
            "auth",
            "-d", dispenser_url,
        ], cwd=tool_dir)
        return True

    # Check if auth files already exist from a previous session
    auth_arm64 = Path.home() / ".gplay-auth.json"
    if auth_arm64.exists():
        print(f"[AUTH] Found existing auth file at {auth_arm64}")
        return True

    print("[WARN] No authentication credentials found in environment!")
    print("Please set GPLAY_EMAIL and GPLAY_AAS_TOKEN, or DISPENSER_URL.")
    return False


def bundle_as_apkm(apk_files, target_apkm_path):
    """Bundle multiple APK files into a single .apkm (ZIP) archive."""
    print(f"[BUNDLE] Packaging {len(apk_files)} APKs into {target_apkm_path}...")
    with zipfile.ZipFile(target_apkm_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for apk in apk_files:
            zf.write(apk, arcname=apk.name)
    print(f"[BUNDLE] Created bundle: {target_apkm_path} ({os.path.getsize(target_apkm_path):,} bytes)")


def process_app(app_config, tool_dir, final_out_dir):
    """Download and package a single app entry."""
    package = app_config.get("package")
    if not package:
        print("[ERROR] App entry missing 'package' field. Skipping.")
        return False

    arch = app_config.get("arch", "arm64")
    format_type = app_config.get("format", "apkm").lower()  # "apkm" or "apk"
    version_code = app_config.get("version")
    output_name = app_config.get("output_name")

    print(f"\n=======================================================")
    print(f"[APP] Processing: {package} (arch={arch}, format={format_type})")
    print(f"=======================================================")

    gplay_script = tool_dir / "gplay-downloader.py"

    # Temporary directory for this app's download artifacts
    with tempfile.TemporaryDirectory(prefix=f"gplay_{package}_") as temp_dir:
        temp_path = Path(temp_dir)
        cmd = [
            sys.executable,
            str(gplay_script),
            "download",
            package,
            "-a", arch,
            "-o", str(temp_path),
        ]

        # If format is "apk" (not apkm), we want merged APK
        if format_type == "apk" or app_config.get("merge", False):
            cmd.append("-m")

        if version_code:
            cmd.extend(["-v", str(version_code)])

        ret = run_cmd(cmd, cwd=tool_dir, check=False)
        if ret != 0:
            print(f"[ERROR] Failed to download {package}.")
            return False

        # Gather downloaded apk files in temp_path
        downloaded_apks = sorted(list(temp_path.glob("*.apk")))
        if not downloaded_apks:
            print(f"[ERROR] No APK files downloaded for {package}.")
            return False

        final_out_dir.mkdir(parents=True, exist_ok=True)

        # Case 1: apkm requested and split files exist
        if format_type == "apkm":
            # Check if splits exist or single apk
            if len(downloaded_apks) > 1:
                # Target name
                if not output_name:
                    output_name = f"{package}-latest-{arch}.apkm"
                elif not output_name.endswith(".apkm"):
                    output_name = output_name.rsplit(".", 1)[0] + ".apkm"

                dest_file = final_out_dir / output_name
                bundle_as_apkm(downloaded_apks, dest_file)
            else:
                # App has no splits, it is a standalone APK
                single_apk = downloaded_apks[0]
                if not output_name:
                    output_name = f"{package}-latest-{arch}.apk"
                else:
                    # Switch .apkm extension to .apk since it's not a bundle
                    if output_name.endswith(".apkm"):
                        output_name = output_name[:-5] + ".apk"

                dest_file = final_out_dir / output_name
                shutil.copy2(single_apk, dest_file)
                print(f"[STANDALONE] App has no splits. Saved as APK: {dest_file}")

        # Case 2: apk requested
        else:
            # When -m was passed, gplay-downloader creates *-merged.apk if splits existed,
            # or single APK if no splits existed.
            merged_apks = list(temp_path.glob("*-merged.apk"))
            source_apk = merged_apks[0] if merged_apks else downloaded_apks[0]

            if not output_name:
                output_name = f"{package}-latest-{arch}.apk"
            elif not output_name.endswith(".apk"):
                output_name = output_name.rsplit(".", 1)[0] + ".apk"

            dest_file = final_out_dir / output_name
            shutil.copy2(source_apk, dest_file)
            print(f"[MERGED/APK] Saved APK: {dest_file}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Download Google Play apps defined in config.")
    parser.add_argument("--config", "-c", default="apps.json", help="Path to config JSON file")
    parser.add_argument("--tool-dir", "-t", default="gplay_tool", help="Directory where gplay-downloader.py resides")
    parser.add_argument("--out-dir", "-o", default=None, help="Output directory override")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[FATAL] Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    tool_dir = Path(args.tool_dir).resolve()
    if not tool_dir.exists():
        print(f"[FATAL] Tool directory not found: {tool_dir}")
        sys.exit(1)

    out_dir_str = args.out_dir or config.get("options", {}).get("outDir", "downloads")
    final_out_dir = Path(out_dir_str).resolve()

    # Authenticate
    auth_success = authenticate(tool_dir)
    if not auth_success:
        print("[ERROR] Authentication step did not complete. Attempting downloads anyway...")

    apps = config.get("apps", [])
    if not apps:
        print("[WARN] No apps found in configuration.")
        return

    success_count = 0
    fail_count = 0

    for app in apps:
        ok = process_app(app, tool_dir, final_out_dir)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    print("\n=======================================================")
    print(f"[DONE] Completed: {success_count} succeeded, {fail_count} failed.")
    print("=======================================================")

    if fail_count > 0 and success_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
