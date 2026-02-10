#!/usr/bin/env python3
"""
Folder Scanner CLI Tool
Scans a folder and generates a summary report:
- Total number of files
- Total size of all files
- Largest file (name and size)
- File types breakdown (count per extension)
Saves the report to a text file.
"""

import os
import sys
from datetime import datetime
from collections import Counter


def format_size(size_bytes):
    """Convert bytes to a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def scan_folder(folder_path):
    """Scan all files in a folder and return summary data."""
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        sys.exit(1)

    total_files = 0
    total_size = 0
    largest_file_name = None
    largest_file_size = 0
    extension_counter = Counter()

    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if not os.path.isfile(full_path):
            continue

        total_files += 1
        file_size = os.path.getsize(full_path)
        total_size += file_size

        if file_size > largest_file_size:
            largest_file_size = file_size
            largest_file_name = entry

        _, ext = os.path.splitext(entry)
        ext = ext.lower() if ext else "(no extension)"
        extension_counter[ext] += 1

    return {
        "total_files": total_files,
        "total_size": total_size,
        "largest_file_name": largest_file_name,
        "largest_file_size": largest_file_size,
        "extensions": extension_counter,
    }


def build_report(folder_path, data):
    """Build a human-readable report string."""
    lines = []
    lines.append("=" * 50)
    lines.append("        FOLDER SCAN REPORT")
    lines.append("=" * 50)
    lines.append(f"Folder scanned : {os.path.abspath(folder_path)}")
    lines.append(f"Scan date      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("-" * 50)
    lines.append(f"Total files    : {data['total_files']}")
    lines.append(f"Total size     : {format_size(data['total_size'])}")

    if data["largest_file_name"]:
        lines.append(
            f"Largest file   : {data['largest_file_name']} "
            f"({format_size(data['largest_file_size'])})"
        )
    else:
        lines.append("Largest file   : (none — folder is empty)")

    lines.append("-" * 50)
    lines.append("File types breakdown:")

    if data["extensions"]:
        for ext, count in sorted(data["extensions"].items()):
            lines.append(f"  {ext:20s} : {count} file(s)")
    else:
        lines.append("  (no files found)")

    lines.append("=" * 50)
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python folder_scanner.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    data = scan_folder(folder_path)
    report = build_report(folder_path, data)

    # Print to console
    print(report)

    # Save to file
    report_file = "scan_report.txt"
    with open(report_file, "w") as f:
        f.write(report + "\n")

    print(f"\nReport saved to: {os.path.abspath(report_file)}")


if __name__ == "__main__":
    main()
