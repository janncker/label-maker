#!/usr/bin/env python

from labelmaker_encode import encode_raster_transfer, read_png

import binascii
import packbits
import bluetooth
import sys
import time
import contextlib

STATUS_OFFSET_BATTERY = 6
STATUS_OFFSET_EXTENDED_ERROR = 7
STATUS_OFFSET_ERROR_INFO_1 = 8
STATUS_OFFSET_ERROR_INFO_2 = 9
STATUS_OFFSET_STATUS_TYPE = 18
STATUS_OFFSET_PHASE_TYPE = 19
STATUS_OFFSET_NOTIFICATION = 22

STATUS_TYPE = [
    "Reply to status request",
    "Printing completed",
    "Error occured",
    "IF mode finished",
    "Power off",
    "Notification",
    "Phase change",
]

STATUS_BATTERY = [
    "Full",
    "Half",
    "Low",
    "Change batteries",
    "AC adapter in use"
]

@contextlib.contextmanager
def BluetoothSocketManager(*args, **kwargs):
    sock = bluetooth.BluetoothSocket(*args, **kwargs)
    yield sock
    sock.close()

def print_status(raw):
    if len(raw) != 32:
        print(f"Error: status must be 32 bytes. Got {len(raw)}")
        return

    if raw[STATUS_OFFSET_STATUS_TYPE] < len(STATUS_TYPE):
        print(f"Status: {STATUS_TYPE[raw[STATUS_OFFSET_STATUS_TYPE]]}")
    else:
        print(f"Status: 0x{raw[STATUS_OFFSET_STATUS_TYPE]:02x}")

    if raw[STATUS_OFFSET_BATTERY] < len(STATUS_BATTERY):
        print(f"Battery: {STATUS_BATTERY[raw[STATUS_OFFSET_BATTERY]]}")
    else:
        print(f"Battery: 0x{raw[STATUS_OFFSET_BATTERY]:02x}")

    print(f"Error info 1: 0x{raw[STATUS_OFFSET_ERROR_INFO_1]:02x}")
    print(f"Error info 2: 0x{raw[STATUS_OFFSET_ERROR_INFO_2]:02x}")
    print(f"Extended error: 0x{raw[STATUS_OFFSET_EXTENDED_ERROR]:02x}")
    print()


# Check for input image
if len(sys.argv) < 3:
    print("Usage: %s <path-to-image> <bdaddr> [ch]" % sys.argv[0])
    sys.exit(1)

addr = sys.argv[2]
if len(sys.argv) < 4:
    ch = 1
else:
    ch = sys.argv[3]
# Get bluetooth socket
with BluetoothSocketManager(bluetooth.RFCOMM) as ser:
    ser.connect((addr, ch))

    # Read input image into memory
    data = read_png(sys.argv[1])

    # Enter raster graphics (PTCBP) mode
    ser.send(b"\x1b\x69\x61\x01")

    # Initialize
    ser.send(b"\x1b\x40")

    # Dump status
    ser.send(b"\x1b\x69\x53")
    print_status( ser.recv(32) )

    # Flush print buffer
    ser.send(b"\x00" * 64)

    # Initialize
    ser.send(b"\x1b\x40")

    # Enter raster graphics (PTCBP) mode
    ser.send(b"\x1b\x69\x61\x01")

    # Found docs on http://www.undocprint.org/formats/page_description_languages/brother_p-touch
    ser.send(b"\x1B\x69\x7A") # Set media & quality
    ser.send(b"\xC4\x01") # print quality, continuous roll
    ser.send(b"\x0C") # Tape width in mm
    ser.send(b"\x00") # Label height in mm (0 for continuous roll)

    # Number of raster lines in image data
    raster_lines = len(data) >> 4
    ser.send(raster_lines.to_bytes(2, 'little'))

    # Unused data bytes in the "set media and quality" command
    ser.send(b"\x00\x00\x00\x00")

    # Set print chaining off (0x8) or on (0x0)
    ser.send(b"\x1B\x69\x4B\x08")

    # Set no mirror, no auto tape cut
    ser.send(b"\x1B\x69\x4D\x00")

    # Set margin amount (feed amount)
    ser.send(b"\x1B\x69\x64\x00\x00")

    # Set compression mode: TIFF
    ser.send(b"\x4D\x02")

    # Send image data
    print("Sending image data")
    for line in encode_raster_transfer(data):
        ser.send( line )
    print("Done")

    # Print and feed
    ser.send(b"\x1A")

    # Dump status that the printer returns
    print_status( ser.recv(32) )

    # Initialize
    ser.send(b"\x1b\x40")
