#!/usr/bin/env python3
"""
Filter-by-extension add-on for the folder scanner.

Usage examples:
    # Show only .py and .txt files in a folder
    python filter_by_extension.py test_scan_me --ext .py .txt

    # Show only .csv files and save the report
    python filter_by_extension.py test_scan_me --ext .csv -o filtered_report.txt

    # Exclude .bin files from the scan
    python filter_by_extension.py test_scan_me --exclude .bin
"""

import argparse
from pathlib import Path
from collections import defaultdict

from typing import Optional

from folder_report import format_size


def scan_folder_filtered(folder_path: str, extensions: Optional[list] = None,
                         exclude: Optional[list] = None) -> dict:
    """Scan folder and collect file stats, filtered by extension.

    Args:
        folder_path: Path to the folder to scan.
        extensions: If provided, only include files with these extensions.
        exclude: If provided, exclude files with these extensions.
    """
    root = Path(folder_path).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")

    # Normalize extensions to lowercase with leading dot
    if extensions:
        extensions = [e if e.startswith(".") else f".{e}" for e in extensions]
        extensions = [e.lower() for e in extensions]
    if exclude:
        exclude = [e if e.startswith(".") else f".{e}" for e in exclude]
        exclude = [e.lower() for e in exclude]

    total_files = 0
    total_size = 0
    largest_file = None
    largest_size = 0
    by_extension = defaultdict(lambda: {"count": 0, "size": 0})
    skipped = 0

    for entry in root.rglob("*"):
        if not entry.is_file():
            continue

        ext = entry.suffix.lower() or "(no extension)"

        # Apply include filter
        if extensions and ext not in extensions:
            skipped += 1
            continue

        # Apply exclude filter
        if exclude and ext in exclude:
            skipped += 1
            continue

        total_files += 1
        try:
            size = entry.stat().st_size
        except OSError:
            size = 0
        total_size += size
        if size >= largest_size:
            largest_size = size
            largest_file = entry
        by_extension[ext]["count"] += 1
        by_extension[ext]["size"] += size

    return {
        "folder": str(root),
        "total_files": total_files,
        "total_size": total_size,
        "largest_file": largest_file,
        "largest_size": largest_size,
        "by_extension": dict(by_extension),
        "skipped": skipped,
        "filter_include": extensions,
        "filter_exclude": exclude,
    }


def build_filtered_report(data: dict) -> str:
    """Build a report that shows the active filters."""
    lines = [
        "=" * 60,
        "FOLDER SCAN REPORT (FILTERED)",
        "=" * 60,
        f"Folder: {data['folder']}",
        "",
    ]

    if data["filter_include"]:
        lines.append(f"Include extensions: {', '.join(data['filter_include'])}")
    if data["filter_exclude"]:
        lines.append(f"Exclude extensions: {', '.join(data['filter_exclude'])}")
    lines.append(f"Files skipped by filter: {data['skipped']}")

    lines += [
        "",
        "SUMMARY",
        "-" * 40,
        f"Total files (after filter):  {data['total_files']}",
        f"Total size  (after filter):  {format_size(data['total_size'])}",
        "",
    ]

    if data["largest_file"] is not None:
        lines.append(
            f"Largest file: {data['largest_file'].name} ({format_size(data['largest_size'])})"
        )
        lines.append(f"  Path: {data['largest_file']}")
    else:
        lines.append("Largest file: (none)")

    lines += [
        "",
        "FILE TYPES BREAKDOWN",
        "-" * 40,
    ]
    for ext in sorted(data["by_extension"].keys()):
        info = data["by_extension"][ext]
        lines.append(f"  {ext:20}  count: {info['count']:6}  size: {format_size(info['size'])}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan a folder with optional file-extension filtering."
    )
    parser.add_argument("folder", type=str, help="Path to the folder to scan")
    parser.add_argument(
        "--ext", nargs="+", default=None,
        help="Only include files with these extensions (e.g. --ext .py .txt)"
    )
    parser.add_argument(
        "--exclude", nargs="+", default=None,
        help="Exclude files with these extensions (e.g. --exclude .bin .log)"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Save report to this file"
    )
    parser.add_argument(
        "--no-save", action="store_true",
        help="Print report to stdout only, do not save to file"
    )
    args = parser.parse_args()

    if args.ext and args.exclude:
        parser.error("Use --ext or --exclude, not both at the same time.")

    try:
        data = scan_folder_filtered(args.folder, extensions=args.ext, exclude=args.exclude)
    except NotADirectoryError as e:
        print(f"Error: {e}")
        return 1

    report = build_filtered_report(data)
    print(report)

    if not args.no_save:
        if args.output:
            out_path = Path(args.output)
        else:
            folder_name = Path(args.folder).name or "root"
            out_path = Path(args.folder) / f"filtered_report_{folder_name}.txt"
        out_path = Path(out_path).resolve()
        out_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {out_path}")

    return 0


if __name__ == "__main__":
    exit(main())
