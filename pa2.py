import sys
import os
import json
import yaml
from pathlib import Path
import xml.etree.ElementTree as ET


class InputError(Exception):
    """just used for invalid input files"""

# I'm just using this class to act as the file handler.
class filecheck():

    def __init__(self, yaml_path, xml_path):
        self.yaml_file = Path(yaml_path)
        self.xml_file = Path(xml_path)
    # tries to load both files
    def file_load(self):
        try:
            with self.yaml_file.open("r") as file:
                yaml_loader = yaml.safe_load(file)
            with self.xml_file.open("r") as file:
                xml_loader = ET.parse(file)

            return yaml_loader, xml_loader
        # handles exceptions that occur
        except (OSError, yaml.YAMLError, ET.ParseError) as e:
            raise InputError(
                f"Unable to continue because of: {e}"
            ) from e

    # using this function to do the conversion from xml and yaml to json
    def comparison(self):
        violations = []
        compliant = []
        interfaces = []
        up = 0
        down = 0
        other = 0
        total_devices = 0
        skipped_devices = 0

        with self.yaml_file.open("r") as file:
            yamlsafeload = yaml.safe_load(file)
        with self.xml_file.open("r") as file:
            xmlsafeload = ET.parse(file)

        root_finder = xmlsafeload.getroot()
        for device in root_finder.findall("device"):
            device_info = device.attrib.copy()
            print(device_info)
            if yamlsafeload["require_owner"] and device.find("owner") is None:
                violations.append(device_info)
                skipped_devices += 1
                total_devices += 1
            else:
                compliant.append(device_info)
                total_devices += 1
            for interface in device.findall("interface"):
                status = interface.get("status")
                # The actual if statement to count
                if status == "up":
                     up += 1
                elif status == "down":
                    down += 1
                else:
                    other += 1
                # trying to get the interfaces list setup
        interfaces.append(["up: ", up, "down: ", down, "other: ", other])

        return violations, compliant, total_devices, skipped_devices, interfaces

# The actual code for main
def main():
    # I had tested the error handling without this try and except and the print out was an eyesore
    try:
        initial_check = filecheck(sys.argv[1], sys.argv[2])
        yaml_fileout, xml_fileout = initial_check.file_load()
        print(yaml_fileout)
    # Only the error explanation that I made prints now.
    except InputError as e:
        print(e)

    printing = filecheck(sys.argv[1], sys.argv[2])
    json_print = printing.comparison()
    print(json_print)

# my attempt at running main
main()
