#!/usr/bin/env python3

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import sys


def getSize(txt, font):
    testImg = Image.new('L', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)


MARGIN_H = 4
MARGIN_V = 4

IMG_STD_HEIGHT = 128


def draw_text(text, fontfile = None, vertical = None, fontsize = None):
    if not fontfile:
        fontfile = './yahei.ttf'

    if vertical:

        if fontsize:
            font = ImageFont.truetype(fontfile, fontsize)
            width, height = getSize(text, font)
            if width + MARGIN_H  > IMG_STD_HEIGHT :
                print("String size is too long to print in one line")
                sys.exit(-1)
        else:
            fontsize = 5
            width = 5
            while width < IMG_STD_HEIGHT - MARGIN_H :
                font = ImageFont.truetype(fontfile, fontsize)
                width, height = getSize(text, font)
                fontsize  = fontsize + 1
        print(width, height)
        img_width = IMG_STD_HEIGHT
        img_height = height + MARGIN_V

        img = Image.new("L", (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        #draw.text(( MARGIN_H / 2, (IMG_STD_HEIGHT - MARGIN_H - width) /2 ), text, font = font)
        draw.text((( IMG_STD_HEIGHT - MARGIN_H -width ) / 2, MARGIN_V /2), text, font = font)
        img = img.rotate(90, expand=True)


    else:
        fontsize = 10
        height = 10
        while height < IMG_STD_HEIGHT - MARGIN_V :
            font = ImageFont.truetype(fontfile, fontsize)
            width, height = getSize(text, font)
            fontsize  = fontsize + 1

        img_width = width + MARGIN_H
        img_height = IMG_STD_HEIGHT

        img = Image.new("L", (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        draw.text(( MARGIN_H / 2, MARGIN_V /2 ), text, font = font)

    return img




if __name__ == '__main__':

    text = sys.argv[1]

    img = draw_text(text, vertical = True, fontsize = 20)
    print(img.width, img.height)
    img.save("./image.png")
