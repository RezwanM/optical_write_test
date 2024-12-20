#!/usr/bin/python

import os
import subprocess
import time

from pathlib import Path


class GenericUtils:
    def __init__(
        self, temp_dir: str, sample_file_path: str, sample_file: str, md5sum_file: str
    ):
        self.temp_dir = temp_dir
        self.sample_file_path = sample_file_path
        self.sample_file = sample_file
        self.md5sum_file = md5sum_file

    def create_working_dirs(self) -> int:
        """Create the working directory

        Returns:
            The exit code for the function
        """
        # First, create the temp dir and cd there
        print("Creating Temp directory and moving there ...")
        try:
            subprocess.run(
                ["mkdir", "-p", self.temp_dir], capture_output=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            return 1
        try:
            subprocess.run(["cd", self.temp_dir], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            return 1
        print("Now working in {Path.cwd()} ...")
        return 0

    def get_sample_data(self) -> int:
        """Copy the sample files to the working directory

        Returns:
            The exit code for the copy process
        """
        # Get our sample files
        print(f"Getting sample files from {self.sample_file_path} ...")
        try:
            result = subprocess.run(
                ["cp", "-a", self.sample_file_path + self.sample_file, self.temp_dir],
                capture_output=True,
                check=True,
            )
            rt = result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
        return rt

    def generate_md5(self) -> int:
        """Generate the md5sums for sample files

        Returns:
            The exit code for the md5sum check
        """
        # Generate the md5sum
        print("Generating md5sums of sample files ...")
        cur_dir = Path.cwd()
        try:
            subprocess.run(["cd", self.sample_file], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            return 1
        try:
            subprocess.run(
                ["md5sum", "--", "*", ">", self.temp_dir + "/" + self.md5sum_file],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            return 1
        # Check the sums for paranoia sake
        rt = GenericUtils.check_md5(self.temp_dir + "/" + self.md5sum_file)
        try:
            subprocess.run(["cd", cur_dir], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            os._exit(1)
        return rt

    @staticmethod
    def check_md5(file: str) -> int:
        """Check an md5sum file

        Args:
            file: An md5sum file

        Returns:
            The exit code for the md5sum check
        """
        print("Checking md5sums ...")
        try:
            result = subprocess.run(
                ["md5sum", "-c", file], capture_output=True, check=True
            )
            rt = result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
        return rt


class DiskUtils:
    def __init__(
        self,
        temp_dir: str,
        iso_name: str,
        sample_file: str,
        md5sum_file: str,
        start_dir: str,
        optical_drive: str,
        optical_type: str,
    ):
        self.temp_dir = temp_dir
        self.iso_name = iso_name
        self.sample_file = sample_file
        self.md5sum_file = md5sum_file
        self.optical_drive = optical_drive
        self.optical_type = optical_type

    def generate_iso(self) -> int:
        """Generate an ISO file

        Returns:
            The exit code for the ISO generation process
        """
        # Generate ISO image
        print("Creating ISO Image ...")
        try:
            result = subprocess.run(
                [
                    "genisoimage",
                    "-input-charset",
                    "UTF-8",
                    "-r",
                    "-J",
                    "-o",
                    self.iso_name,
                    self.sample_file,
                ],
                capture_output=True,
                check=True,
            )
            rt = result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
        return rt

    def burn_iso(self) -> int:
        """Burn an ISO image

        Returns:
            The exit code for the ISO burning process
        """
        # Burn the ISO with the appropriate tool
        print("Sleeping 10 seconds in case drive is not yet ready ...")
        time.sleep(10)
        print("Beginning image burn ...")
        if self.optical_type == "cd":
            try:
                result = subprocess.run(
                    ["wodim", "-eject", f"dev={self.optical_drive}", self.iso_name],
                    capture_output=True,
                    check=True,
                )
                rt = result.returncode
            except subprocess.CalledProcessError as e:
                print(f"Command failed with exit code {e.returncode}")
                print(e.stderr)
                rt = e.returncode
        elif self.optical_type == "dvd" or self.optical_type == "bd":
            try:
                result = subprocess.run(
                    [
                        "growisofs",
                        "-dvd-compat",
                        "-Z",
                        f"{self.optical_drive}={self.iso}",
                    ],
                    capture_output=True,
                    check=True,
                )
                rt = result.returncode
            except subprocess.CalledProcessError as e:
                print(f"Command failed with exit code {e.returncode}")
                print(e.stderr)
                rt = e.returncode
        else:
            print(f"Invalid type specified {self.optical_type}")
            os._exit(1)
        return rt

    def check_disk(self) -> int:
        """Check a newly-created disk

        Returns:
            The exit code for the md5sum check
        """
        timeout = 300
        sleep_count = 0
        interval = 3

        # Give the tester up to 5 minutes to reload the newly created CD/DVD
        print("Waiting up to 5 minutes for drive to be mounted ...")
        while True:
            time.sleep(interval)
            sleep_count += interval
            try:
                result = subprocess.run(
                    [
                        "mount",
                        self.optical_drive,
                        "2>&1",
                        "|",
                        "grep",
                        "-E",
                        "-q",
                        "already mounted",
                    ],
                    capture_output=True,
                    check=True,
                )
                rt = result.returncode
            except subprocess.CalledProcessError as e:
                print(f"Command failed with exit code {e.returncode}")
                print(e.stderr)
                rt = e.returncode
            if rt == 0:
                print("Drive appears to be mounted now")
                break
            # If they exceed the timeout limit, make a best effort to load the tray
            # in the next steps
            if sleep_count >= timeout:
                print("WARNING: TIMEOUT Exceeded and no mount detected!")
                break
        print("Deleting original data files ...")
        try:
            subprocess.run(
                ["rm", "-rf", self.sample_file], capture_output=True, check=True
            )
            rt = result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
        if subprocess.run(
            ["mount", "|", "grep", "-q", self.optical_drive],
            capture_output=True,
            check=True,
        ).returncode:
            try:
                mount_pt = subprocess.run(
                    ["mount", "|", "grep", self.optical_drive, "awk", "'{print $3}'"],
                    capture_output=True,
                    check=True,
                ).stdout
                print(f"Disk is mounted to {mount_pt}")
                rt = result.returncode
            except subprocess.CalledProcessError as e:
                print(f"Command failed with exit code {e.returncode}")
                print(e.stderr)
                rt = e.returncode
        else:
            print(f"Attempting best effort to mount {self.optical_drive} on my own")
            mount_pt = self.temp_dir + "/" + "mnt"
            print(f"Creating temp mount point: {mount_pt} ...")
            try:
                subprocess.run(["mkdir", mount_pt], capture_output=True, check=True)
                print("Mounting disk to mount point ...")
                rt = result.returncode
            except subprocess.CalledProcessError as e:
                print(f"Command failed with exit code {e.returncode}")
                print(e.stderr)
                rt = e.returncode
            try:
                result = subprocess.run(
                    ["mount", self.optical_drive, mount_pt],
                    capture_output=True,
                    check=True,
                )
                rt = result.returncode
            except subprocess.CalledProcessError as e:
                print(f"Command failed with exit code {e.returncode}")
                print(e.stderr)
                rt = e.returncode

            if rt != 0:
                msg = f"ERROR: Unable to re-mount {self.optical_drive}!"
                subprocess.run(["echo", msg, ">&2"], capture_output=True, check=True)
                return 1
        print("Copying files from ISO ...")
        try:
            subprocess.run(
                ["cp", mount_pt + "/" + "*", self.temp_dir],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
        return GenericUtils.check_md5(self.md5sum_file)

    def cleanup(self) -> int:
        """Cleaning up work files and directories

        Returns:
            The exit code for the function
        """
        print("Moving back to original location")
        try:
            subprocess.run(["cd", self.start_dir], capture_output=True, check=True)
            rt = e.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
            os._exit(1)
        print(f"Now residing in {Path.cwd()}")
        print("Cleaning up ...")
        try:
            subprocess.run(["unmount", mount_pt], capture_output=True, check=True)
            rt = e.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
        try:
            subprocess.run(
                ["rm", "-fr", self.temp_dir], capture_output=True, check=True
            )
            rt = e.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
        print("Ejecting spent media ...")
        try:
            subprocess.run(
                ["eject", self.optical_drive], capture_output=True, check=True
            )
            rt = e.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(e.stderr)
            rt = e.returncode
        return rt

    def failed(self, msg: str):
        """Trying to perform cleanup() before exiting with error code

        Args:
            msg: The message to be displayed
        """
        print(msg)
        print("Attempting to clean up ..")
        self.cleanup()
        os._exit(1)
