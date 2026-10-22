import sys
import os
import json
import xml
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

# The actual code for main
def main():
    # I had tested the error handling without this try and except and the print out was an eyesore
    try:
        initial_check = filecheck(sys.argv[1], sys.argv[2])
        yaml_fileout, xml_fileout = initial_check.file_load()
        xml_root = xml_fileout.getroot()
        print(yaml_fileout)
        print(xml_root.findall('.//device'))
        print(xml_root.findall('.//interface'))
    # Only the error explanation that I made prints now.
    except InputError as e:
        print(e)

# my attempt at running main
main()
