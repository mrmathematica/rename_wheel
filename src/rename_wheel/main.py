import argparse
from email.parser import Parser
from email.generator import Generator
import os
import tempfile
import wheel.cli.pack as pack
import wheel.cli.unpack as unpack
from wheel.wheelfile import WheelFile
import re


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def filename(name):
    return re.sub("-", "_", name)


def main():
    parser = argparse.ArgumentParser(description="Change Python wheel package name.")
    parser.add_argument("WHEEL_FILE", help="Path to wheel file.")
    parser.add_argument("PACKAGE_NAME", help="New package name.")

    args = parser.parse_args()
    name = normalize(args.PACKAGE_NAME)

    with WheelFile(args.WHEEL_FILE) as wf:
        namever = wf.parsed_filename.group("namever")
        ver = wf.parsed_filename.group("ver")
        dist_info = wf.dist_info_path

    with tempfile.TemporaryDirectory() as working_dir:
        unpack.unpack(args.WHEEL_FILE, working_dir)
        folder = os.path.join(working_dir, namever)

        with open(os.path.join(folder, dist_info, "METADATA"), 'r') as metadata:
            msg = Parser().parse(metadata)
        del msg['Name']
        msg['Name'] = name
        with open(os.path.join(folder, dist_info, "METADATA"), 'w') as metadata:
            Generator(metadata, maxheaderlen=0).flatten(msg)

        os.rename(os.path.join(folder, dist_info), os.path.join(folder, "%s-%s.dist-info" % (filename(name), ver)))

        pack.pack(folder, "", None)
