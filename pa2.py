import sys
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

    # using this function to do the conversion from xml and yaml to json to dump the data
    def comparison(self):
        violations = []
        compliant = []
        interfaces = []
        up = 0
        down = 0
        other = 0
        total_devices = 0
        skipped_devices = 0
        # opens the files
        with self.yaml_file.open("r") as file:
            yamlsafeload = yaml.safe_load(file)
        with self.xml_file.open("r") as file:
            xmlsafeload = ET.parse(file)

        root_finder = xmlsafeload.getroot()
        for device in root_finder.findall("device"):
            total_devices += 1
            device_info = device.attrib.copy()
            # determining what device and OS it is because how else would I do this?
            device_role = device.get("role")
            device_OS = device.get("os")
            # had to use an if statement with two variables for OS checks to store both properly for the comparison
            if device_role in yamlsafeload["min_os"] and device_OS is not None:
                device_OS = tuple(int(part) for part in device_OS.split("."))
                min_OS = tuple(int(part) for part in yamlsafeload["min_os"][device_role].split("."))
                # the part that actually does the checks
                if device_OS < min_OS or yamlsafeload["require_owner"] and device.find("owner") is None:
                    violations.append(device_info)
                # if no violation conditions are met, it adds the device to the compliant list
                else:
                    compliant.append(device_info)
            else:
                skipped_devices += 1
            # gets the interface info as needed by looking for the interface instance
            for interface in device.findall("interface"):
                status = interface.get("status")
                # The actual if statement to count
                if status == "up":
                     up += 1
                elif status == "down":
                    down += 1
                else:
                    other += 1

        # formats the interfaces list all nice
        interfaces.append(f"up: {up}, down: {down}, other: {other}")
        # puts all the data together because it would be a pain to do this another way
        dump_data = {
            "Compliant": compliant,
            "Interfaces": interfaces,
            "Violations": violations,
            "Total Devices": total_devices,
            "Skipped Devices": skipped_devices
        }
        # actually puts the data into the file
        with open("audit.json", "w") as file:
            json.dump(dump_data, file, indent=2)
        # had to actually return something during testing. I don't even know why I still kept it in
        return violations, compliant, total_devices, skipped_devices, interfaces

# The actual code for main
def main():
    # I had tested the error handling without this try and except and the print out was an eyesore
    try:
        initial_check = filecheck(sys.argv[1], sys.argv[2])
        yaml_fileout, xml_fileout = initial_check.file_load()
        print("yaml contents: ", yaml_fileout, "xml contents: ", xml_fileout)
    # Only the error explanation that I made prints now.
    except InputError as e:
        print(e)

    # it was the only way I could think of to call the function. there's probably a more elegant solution
    printing = filecheck(sys.argv[1], sys.argv[2])
    json_print = printing.comparison()
    print(json_print)
    print("wait, it actually worked?")
    sys.exit(0)

# my attempt at running main. Don't ask why
main()
