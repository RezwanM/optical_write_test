#!/usr/bin/python

import argparse
import os
import subprocess

from pathlib import Path
from utils import GenericUtils, DiskUtils

temp_dir = "/tmp/optical-test"
iso_name = "optical-test.iso"
sample_file_path = "/usr/share/example-content/"
sample_file = "Ubuntu_Free_Culture_Showcase"
md5sum_file = "optical_test.md5"
start_dir = Path.cwd()

# Parse positional arguments
parser = argparse.ArgumentParser()
parser.add_argument("optical_drive", type=Path, default="/dev/sr0")
parser.add_argument("optical_type", type=str, default="cd")
args = parser.parse_args()
if os.path.exists(args.optical_drive):
    try:
        optical_drive = subprocess.run(
            ["readlink", "-f", args.optical_drive], capture_output=True, check=True
        ).stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(e.stderr)
if args.optical_type:
    optical_type = args.optical_type

# Create objects
gen = GenericUtils(temp_dir, sample_file_path, sample_file, md5sum_file)
disk = DiskUtils(
    temp_dir, iso_name, sample_file, md5sum_file, start_dir, optical_drive, optical_type
)


if __name__ == "__main__":
    gen.create_working_dirs()
    if gen.create_working_dirs() != 0:
        disk.failed("Failed to create working directories")

    gen.get_sample_data()
    if gen.get_sample_data() != 0:
        disk.failed("Failed to copy sample data")

    gen.generate_md5()
    if gen.generate_md5() != 0:
        disk.failed("Failed to generate initial md5")

    disk.generate_iso()
    if disk.generate_iso() != 0:
        disk.failed("Failed to create ISO image")

    disk.burn_iso()
    if disk.burn_iso() != 0:
        disk.failed("Failed to burn ISO image")

    disk.check_disk()
    if disk.check_disk() != 0:
        disk.failed("Failed to verify files on optical disk")

    disk.cleanup()
    if disk.cleanup() != 0:
        disk.failed("Failed to clean up")

    os._exit(0)
