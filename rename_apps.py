#!/usr/bin/env python3
"""
Automatically analyze downloaded package filenames and rename them based on apps.json mapping rules.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

PACKAGE_EXTENSIONS = {".apk", ".apkm", ".xapk", ".apks", ".zip"}


def load_rules(config_path):
    """Load renaming rules from apps.json."""
    if not config_path.is_file():
        print(f"[INFO] Configuration file '{config_path}' not found. Skipping auto-rename.")
        return []

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to read '{config_path}': {e}. Skipping auto-rename.")
        return []

    rules = []

    # Format 1: { "apps": [ { "package": "...", "output_name": "..." }, ... ] }
    if isinstance(data, dict) and "apps" in data:
        items = data["apps"]
    # Format 2: [ { "package": "...", "output_name": "..." }, ... ]
    elif isinstance(data, list):
        items = data
    # Format 3: { "com.example.app": "custom_name.apk", ... }
    elif isinstance(data, dict):
        items = [{"package": k, "output_name": v} for k, v in data.items() if k != "options"]
    else:
        items = []

    for item in items:
        if not isinstance(item, dict):
            continue
        pkg = item.get("package") or item.get("match") or item.get("id")
        out_name = item.get("output_name") or item.get("name")
        pattern = item.get("pattern") or item.get("regex")
        if (pkg or pattern) and out_name:
            rules.append({
                "package": pkg,
                "output_name": out_name,
                "pattern": pattern
            })

    # Sort rules so more specific/longer matches take priority over short keywords (e.g. 'youtube.music' before 'youtube')
    rules.sort(key=lambda r: len(r.get("package") or r.get("pattern") or ""), reverse=True)
    return rules


def match_file(filename, rule):
    """Check if a filename matches a given rule."""
    fname_lower = filename.lower()

    # Regex matching if defined
    if rule.get("pattern"):
        try:
            if re.search(rule["pattern"], filename, re.IGNORECASE):
                return True
        except re.error:
            pass

    pkg = rule.get("package")
    if not pkg:
        return False

    pkg_lower = pkg.lower()

    # Exact package string match in filename (e.g. com.reddit.frontpage)
    if pkg_lower in fname_lower:
        return True

    # Underscore variant (e.g. com_reddit_frontpage)
    if pkg_lower.replace(".", "_") in fname_lower:
        return True

    # Hyphen variant (e.g. com-reddit-frontpage)
    if pkg_lower.replace(".", "-") in fname_lower:
        return True

    return False


def determine_target_name(source_file, output_template):
    """Determine final filename, harmonizing extensions (e.g. .apk vs .apkm)."""
    src_ext = source_file.suffix.lower()
    out_ext = Path(output_template).suffix.lower()

    target_name = output_template

    # If target has no extension, attach source extension
    if not out_ext:
        target_name = f"{output_template}{src_ext}"
    # If target specifies .apkm but downloaded file is standalone .apk
    elif out_ext == ".apkm" and src_ext == ".apk":
        target_name = str(Path(output_template).with_suffix(".apk"))
    # If target specifies .apk but downloaded file is an .apkm bundle
    elif out_ext == ".apk" and src_ext == ".apkm":
        target_name = str(Path(output_template).with_suffix(".apkm"))

    return target_name


def rename_files(target_dir, rules, dry_run=False):
    """Scan directory and rename files according to rules."""
    if not rules:
        return 0

    target_path = Path(target_dir).resolve()
    if not target_path.is_dir():
        print(f"[ERROR] Target directory '{target_dir}' does not exist.")
        return 0

    renamed_count = 0

    print("===================================================")
    print(f"[RENAME] Analyzing files in: {target_path}")
    print(f"[RENAME] Loaded {len(rules)} rule(s) from configuration.")
    print("===================================================")

    for entry in sorted(target_path.iterdir()):
        if not entry.is_file() or entry.suffix.lower() not in PACKAGE_EXTENSIONS:
            continue

        filename = entry.name

        for rule in rules:
            if match_file(filename, rule):
                target_name = determine_target_name(entry, rule["output_name"])
                dest_path = entry.with_name(target_name)

                if entry == dest_path:
                    print(f"  [=] Already matches: '{filename}'")
                    break

                pkg_label = rule.get("package") or rule.get("pattern")
                if dry_run:
                    print(f"  [*] [DRY-RUN] '{filename}' -> '{target_name}' (matched: '{pkg_label}')")
                else:
                    if dest_path.exists():
                        print(f"  [!] Overwriting existing file: '{target_name}'")
                    os.replace(entry, dest_path)
                    print(f"  [+] Renamed: '{filename}' -> '{target_name}' (matched: '{pkg_label}')")

                renamed_count += 1
                break

    print("===================================================")
    print(f"[RENAME] Completed: {renamed_count} file(s) renamed.")
    print("===================================================")
    return renamed_count


def main():
    parser = argparse.ArgumentParser(description="Rename downloaded package files according to apps.json rules.")
    parser.add_argument("--config", "-c", default="apps.json", help="Path to config JSON file (default: apps.json)")
    parser.add_argument("--dir", "-d", default=".", help="Target directory (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Print planned renames without applying them")
    args = parser.parse_args()

    config_path = Path(args.config)
    rules = load_rules(config_path)
    rename_files(args.dir, rules, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
