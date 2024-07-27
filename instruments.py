# Imports
import sys
import pyvisa
import pyvisa.constants


class Instruments():
    def __init__(self):
        self.rm = pyvisa.ResourceManager()  # Open a VISA resource manager
        print("Using resource manager:", self.rm)
        self.instruments = self._find()

    def _find(self) -> dict:
        resources = self.rm.list_resources()
        found_devices = {}

        for instrument in resources:
            device = self.rm.open_resource(instrument)
            name = device.get_visa_attribute(
                pyvisa.constants.ResourceAttribute.model_name)
            device.close()
            found_devices[name] = instrument

        print("Devices found:", len(found_devices))
        return found_devices

    def open(self, model_name: str):
        device = self.instruments.get(model_name)

        try:
            resource = self.rm.open_resource(device)
        except pyvisa.constants.VI_ERROR_INV_RSRC_NAME:
            print("ERROR: Could not open instrument", model_name, file=sys.stderr)
            return
        else:
            print("Success! Opened:", device)
            return resource

    def close(self, resource):
        try:
            resource.close()
        except pyvisa.constants.VI_ERROR_CLOSING_FAILED:
            print("ERROR: Could not close instrument", resource, file=sys.stderr)
        else:
            print("Closed:", resource)


    def close_all(self):
        if not self.open_resources:
            print("No devices to close")
            return

        for resource in self.rm.list_opened_resources:
            self.close(resource)

        if self.rm.list_opened_resources:
            print("Devices still open:", self.open_resources)