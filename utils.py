#!/usr/bin/python

class GenericUtils:
    def __init__(self):
        pass

    def create_working_dirs(self):
        """Create the working directory"""
        pass

    def get_sample_data(self):
        """Copy the sample files to the working directory"""
        pass

    def generate_md5(self):
        """Generate the md5sums for sample files"""
        pass

    def check_md5(self, file):
        """Check an md5sum file"""
        pass


class DiskUtils:
    def __init__(self):
        pass

    def generate_iso(self):
        """Generate an ISO file"""
        pass

    def burn_iso(self):
        """Burn an ISO image"""
        pass

    def check_disk(self):
        """Check a newly-created disk"""
        pass

    def cleanup(self):
        """Cleaning up work files and directories"""
        pass

    def failed(self, msg):
        """Trying to perform cleanup() before exiting with error code"""
        pass

