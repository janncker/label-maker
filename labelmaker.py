#!/usr/bin/env python

from labelmaker_encode import encode_raster_transfer, read_png

import argparse
import bluetooth
import sys
import contextlib
import ctypes
import ptcbp
import ptstatus

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('image', help='Image file to print.')
    p.add_argument('bdaddr', help='BDADDR of the printer.')
    p.add_argument('-c', '--rfcomm-channel', help='RFCOMM channel.', default=1, type=int)
    p.add_argument('-n', '--no-print', help='Do not send print command.', action='store_true')
    return p, p.parse_args()

def reset_printer(ser):
    # Flush print buffer
    ser.send(b"\x00" * 64)

    # Initialize
    ser.send(ptcbp.serialize_control('reset'))

    # Enter raster graphics (PTCBP) mode
    ser.send(ptcbp.serialize_control('use_command_set', ptcbp.CommandSet.ptcbp))

def configure_printer(ser, raster_lines):
    reset_printer(ser)

    # Set media & quality
    ser.send(ptcbp.serialize_control_obj('set_print_parameters', ptcbp.PrintParameters(
        active_fields=(ptcbp.PrintParameterField.width |
                       ptcbp.PrintParameterField.quality |
                       ptcbp.PrintParameterField.recovery),
        media_type=ptcbp.MediaType.laminated,
        width_mm=12, # Tape width in mm
        length_mm=0, # Label height in mm (0 for continuous roll)
        length_px=raster_lines, # Number of raster lines in image data
        is_follow_up=0, # Unused
        sbz=0, # Unused
    )))

    # Set print chaining off (0x8) or on (0x0)
    ser.send(ptcbp.serialize_control('set_page_mode_advanced', ptcbp.PageModeAdvanced.no_page_chaining))

    # Set no mirror, no auto tape cut
    ser.send(ptcbp.serialize_control('set_page_mode', 0x00))

    # Set margin amount (feed amount)
    ser.send(ptcbp.serialize_control('set_page_margin', 0))

    # Set compression mode: TIFF
    ser.send(ptcbp.serialize_control('compression', ptcbp.CompressionType.rle))

def do_print_job(ser, data, args):
    print('=> Querying printer status...')

    reset_printer(ser)

    # Dump status
    ser.send(ptcbp.serialize_control('get_status'))
    status = ptstatus.unpack_status(ser.recv(32))
    ptstatus.print_status(status)

    if status.err != 0x0000 or status.phase_type != 0x00 or status.phase != 0x0000:
        print('** Printer indicates that it is not ready. Refusing to continue.')
        sys.exit(1)

    print('=> Configuring printer...')

    raster_lines = len(data) // 16
    configure_printer(ser, raster_lines)

    # Send image data
    print(f"=> Sending image data ({raster_lines} lines)...")
    for line in encode_raster_transfer(data):
        ser.send(line)
        sys.stdout.write(line[0:1].decode('ascii'))
        sys.stdout.flush()
    print()
    print("=> Image data was sent successfully. Printing will begin soon.")

    if not args.no_print:
        # Print and feed
        ser.send(ptcbp.serialize_control('print'))

        # Dump status that the printer returns
        status = ptstatus.unpack_status(ser.recv(32))
        ptstatus.print_status(status)

    print("=> All done.")

def main():
    p, args = parse_args()

    # Read input image into memory
    data = read_png(args.image)
    # Get bluetooth socket
    with contextlib.closing(bluetooth.BluetoothSocket(bluetooth.RFCOMM)) as ser:
        print('=> Connecting to printer...')

        ser.connect((args.bdaddr, args.rfcomm_channel))

        try:
            do_print_job(ser, data, args)
        finally:
            # Initialize
            reset_printer(ser)

if __name__ == '__main__':
    main()
