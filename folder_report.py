#!/usr/bin/env python3
"""
Folder Report - A CLI utility for directory analysis.
- Takes a folder path as input
- Scans all files in that folder (recursively)
- Outputs: total files, total size, largest file, file types breakdown
- Saves the report to a text file
- Version: 1.0.0
"""

import argparse
import os
from pathlib import Path
from collections import defaultdict


def format_size(size_bytes: int) -> str:
    """Format size in human-readable form."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def scan_folder(folder_path: str) -> dict:
    """Scan folder and collect file stats. Returns dict with summary data."""
    root = Path(folder_path).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")

    total_files = 0
    total_size = 0
    largest_file = None
    largest_size = 0
    by_extension = defaultdict(lambda: {"count": 0, "size": 0})

    for entry in root.rglob("*"):
        if entry.is_file():
            total_files += 1
            try:
                size = entry.stat().st_size
            except OSError:
                size = 0
            total_size += size
            if size >= largest_size:
                largest_size = size
                largest_file = entry
            ext = entry.suffix.lower() or "(no extension)"
            by_extension[ext]["count"] += 1
            by_extension[ext]["size"] += size

    return {
        "folder": str(root),
        "total_files": total_files,
        "total_size": total_size,
        "largest_file": largest_file,
        "largest_size": largest_size,
        "by_extension": dict(by_extension),
    }


def build_report(data: dict) -> str:
    """Build the report text."""
    lines = [
        "=" * 60,
        "FOLDER SCAN REPORT",
        "=" * 60,
        f"Folder: {data['folder']}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Total files:  {data['total_files']}",
        f"Total size:   {format_size(data['total_size'])}",
        "",
    ]
    if data["largest_file"] is not None:
        lines.append(
            f"Largest file: {data['largest_file'].name} ({format_size(data['largest_size'])})"
        )
        lines.append(f"  Path: {data['largest_file']}")
    else:
        lines.append("Largest file: (none)")
    lines.extend(
        [
            "",
            "FILE TYPES BREAKDOWN",
            "-" * 40,
        ]
    )
    for ext in sorted(data["by_extension"].keys()):
        info = data["by_extension"][ext]
        lines.append(f"  {ext:20}  count: {info['count']:6}  size: {format_size(info['size'])}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan a folder and output a summary report (total files, size, largest file, file types)."
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Path to the folder to scan",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file for the report (default: folder_report_<folder_name>.txt)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print report to stdout only, do not save to file",
    )
    args = parser.parse_args()

    try:
        data = scan_folder(args.folder)
    except NotADirectoryError as e:
        print(f"Error: {e}")
        return 1

    report = build_report(data)
    print(report)

    if not args.no_save:
        if args.output:
            out_path = Path(args.output)
        else:
            folder_name = Path(args.folder).name or "root"
            out_path = Path(args.folder) / f"folder_report_{folder_name}.txt"
        out_path = Path(out_path).resolve()
        out_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {out_path}")

    return 0


if __name__ == "__main__":
    exit(main())
