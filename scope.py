# Imports
import time
import textwrap
import numpy as np
from instruments import Instruments


class Scope():
    def __init__(self, visa_resource):
        ref = visa_resource
        channel = 1
        x-axis
        pass

    def _check_integrity(self):
        pass

    def set_channel(self, channel: int=1):
        # Set source channel
        self.ref.write(f":WAV:SOUR CHAN{channel}")
        self.channel = channel

    def set_trigger(self):
        #TODO: Allow either single or stop
        # Set trigger
        # A stopped screen has best memory depth
        self.ref.write(":SING")
        #self.ref.write(":STOP")

        # Wait for trigger
        trig_status = ""
        while trig_status != "STOP":
            trig_status = self.ref.query(":TRIG:STAT?").strip()
            time.sleep(0.2)

    def get_settings(self):
        # Acquisition settings
        # Fetch acquisition settings from scope
        mem_depth = int(self.ref.query(":ACQ:MDEP?"))
        sample_rate = float(self.ref.query(":ACQ:SRAT?"))
        scale = float(self.ref.query(f":CHAN{self.channel}:SCAL?"))
    #    timescale = scope.query(":TIM:MAIN:SCAL?")
        # Calculate waveform duration
        time_window = mem_depth / sample_rate
        # Calculate time resolution
        time_res = 1/sample_rate
        # Determine time units
        if time_res < 1e-10:
            tUnit = "ns"
        elif time_res < 1e-7:
            tUnit = "us"
        elif time_res < 1e-4:
            tUnit = "ms"
        else:
            tUnit = "s"
        # Generate time axis
        self.x_axis = np.linspace(start=0, stop=time_window, num=int(time_res))

        acq_settings = f"""
            ***********************************
            Acquisition Settings:
            MemDepth        = {mem_depth}
            SampleRate      = {sample_rate}
            DataLength      = {time_window}
            TimeResolution  = {time_res}
            ***********************************
        """
        print(textwrap.dedent(acq_settings))

    def get_waveform(self):
        pass

    def mem_to_screen(self):
        # Truncate raw data to what's on screen, but preserve high-res gained from raw's memory depth
        """
        * Get vertical reference/offset (potentially offscreen)
        * Get vertical scale/step size
        """
        pass