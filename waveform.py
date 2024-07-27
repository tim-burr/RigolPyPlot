#!/usr/bin/env python3

# Imports
import sys
import time
import textwrap
import numpy as np
import matplotlib.pyplot as plot
from instruments import Instruments
from scope import Scope


# Constants
MODEL = "DS1000Z Series"  # Rigol scope model series supported
CHANNEL = 1  # Source data channel


def get_waveform(scope) -> tuple:
    """
    1. STOP
    1. WAV:SOUR CHANn
    2. WAV:MODE RAW  # Works for stopped screen
    3. WAV:FORM BYTE  # Byte format supports highest datapoint transfer in one session (250k)
    3. WAV:STAR start
        a. Set to internal variable to buffer as "start"
            start = 1
    2. **Read memory depth selected
    3. Check if num data points is > 250k
    3.   If so, coerce WAV:STOP 250000
        Else:
            WAV:STOP num_data_points_less_than_250k
    4. WAV:DATA?  # Read
    4. * Loop as needed * Calculate number of loops needed from header, rounding up to nearest integer
        a. Start = Start + 250000  # 250001 to ..
            WAV:STAR start
    """

    # Set source channel
    scope.write(f":WAV:SOUR CHAN{CHANNEL}")

    # Set trigger
    # A stopped screen has best memory depth
    scope.write(":SING")
#    scope.write(":STOP")

    # Wait for trigger
    trig_status = ""
    while trig_status != "STOP":
        trig_status = scope.query(":TRIG:STAT?").strip()
        time.sleep(0.2)

    # Fetch acquisition settings from scope
    mem_depth = int(scope.query(":ACQ:MDEP?"))
    sample_rate = float(scope.query(":ACQ:SRAT?"))
    scale = float(scope.query(f":CHAN{CHANNEL}:SCAL?"))
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
    x_axis = np.linspace(start=0, stop=time_window, num=int(time_res))

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

    # Configure waveform to save
    scope.write(":WAV:MODE RAW")  # Works only for stopped screen
    scope.write(":WAV:FORM BYTE")  # Byte format supports 250k points per read

    # scope.values_format.is_big_endian = False
    # scope.values_format.container = np.array

    # Fetch first waveform data out of loop to get header
    scope.write(":WAV:STAR")
    bytestream = scope.query(":WAV:DATA?")
    # Parse waveform data sections
    header = bytestream[2:11]  # Ignore first two characters
    raw_data = bytestream[12:]
    combined_data = []  # Final stitched-together data (later on)

    # Calculate number of read sessions needed based on max packet size
    sessions = int(np.ceil(float(header) / 250000))

    # TODO: Add looping logic
    for i in range(sessions):
        combined_data.append(raw_data)
        raw_data = scope.query(":WAV:DATA?")[12:]

    # Data integrity check
    print(len(combined_data), time_window)  #TODO: Delete when done with this
    if len(combined_data) != time_window:
        print("ERROR: Missing data detected", file=sys.stderr)
        return

    # Convert byte data to voltages
    scaled_data = combined_data * scale

    return (scaled_data, x_axis, tUnit)

def create_plot(waveform):
    plot.plot(waveform.x_axis, waveform.scaled_data)
    plot.title("Oscilloscope Channel 1")
    plot.ylabel("Voltage (V)")
    plot.xlabel("Time (" + waveform.tUnit + ")")
    plot.xlim(waveform.x_axis[0], waveform.x_axis[-1])
    plot.show()

def main():
    # Open oscilloscope connection
    instruments = Instruments()
    scope = instruments.open(MODEL)

    # Get waveform and plot data
    if scope:
        waveform = get_waveform(scope)
        instruments.close(scope)
        create_plot(waveform)

if __name__ == "__main__":
    main()
    print("Exiting...")