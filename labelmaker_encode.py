import ptcbp
import png
from io import BytesIO

def encode_raster_transfer(data):
    """ Encode 1 bit per pixel image data for transfer over serial to the printer """
    # Send in chunks of 1 line (128px @ 1bpp = 16 bytes)
    # This mirrors the official app from Brother. Other values haven't been tested.
    chunk_size = 16
    zero_line = bytearray(b'\x00' * chunk_size)

    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        if chunk == zero_line:
            yield ptcbp.serialize_control('zerofill')
        else:
            yield ptcbp.serialize_data(chunk, 'rle')

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
