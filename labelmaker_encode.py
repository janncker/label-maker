import packbits
import png
import struct
from io import BytesIO

# "Raster graphics transfer" serial command
TRANSFER_COMMAND = b"G"
ZERO_COMMAND = b"Z"

def encode_raster_transfer(data):
    """ Encode 1 bit per pixel image data for transfer over serial to the printer """
    # Send in chunks of 1 line (128px @ 1bpp = 16 bytes)
    # This mirrors the official app from Brother. Other values haven't been tested.
    chunk_size = 16
    zero_line = bytearray(b'\x00' * chunk_size)

    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        if chunk == zero_line:
            yield ZERO_COMMAND
            continue

        buf = BytesIO()
        # Encode as tiff
        packed_chunk = packbits.encode(chunk)

        # Write header
        buf.write(TRANSFER_COMMAND)

        # Write number of bytes to transfer (n1 + n2*256)
        length = len(packed_chunk)
        buf.write(length.to_bytes(2, 'little'))

        # Write data
        buf.write(packed_chunk)
        yield buf.getvalue()

def decode_raster_transfer(data):
    """ Read data encoded as T encoded as TIFF with transfer headers """

    buf = bytearray()
    i = 0

    while i < len(data):
        if data[i] == TRANSFER_COMMAND:
            # Decode number of bytes to transfer
            num_bytes = int.from_bytes(data[i+1:i+3], little)

            # Copy contents of transfer to output buffer
            transferedData = data[i + 3 : i + 3 + num_bytes]
            buf.extend(transferedData)

            # Confirm
            if len(transferedData) != num_bytes:
                raise Exception("Failed to read %d bytes at index %s: end of input data reached." % (num_bytes, i))

            # Shift to the next position after these command and data bytes
            i = i + 3 + num_bytes

        else:
            raise Exception("Unexpected byte %s" % data[i])

    return buf

def read_png(path):
    """ Read a (monochrome) PNG image and convert to 1bpp raw data

    This should work with any 8 bit PNG. To ensure compatibility, the image can
    be processed with Imagemagick first using the -monochrome flag.
    """

    buf = bytearray()

    # State for bit packing
    bit_cursor = 8
    byte = 0

    # Read the PNG image
    reader = png.Reader(filename=path)
    width, height, rows, metadata = reader.asRGB()

    # Loop over image and pack into 1bpp buffer
    for row in rows:
        for pixel in range(0, len(row), 3):
            bit_cursor -= 1

            if row[pixel] == 0:
                byte |= (1 << bit_cursor)

            if bit_cursor == 0:
                buf.append(byte)
                byte = 0
                bit_cursor = 8

    return buf
