#!/usr/bin/env python3

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
import sys


def getSize(txt, font):
    testImg = Image.new('1', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)


MARGIN_H = 0
MARGIN_V = 0
LABEL_C_MODE_MERGIN = 20
IMG_STD_HEIGHT = 64


def draw_text(text, fontfile = None, vertical = None, fontsize = 0):
    if not fontfile:
        fontfile = './yahei.ttf'

    print(fontfile)


    if vertical:

        if not fontsize:
            fontsize = 10

        font = ImageFont.truetype(fontfile, fontsize)

        total_length = 0
        for item in text.split(" "):

            width , height = getSize(item, font)
            total_length = total_length + height + LABEL_C_MODE_MERGIN

            if width + MARGIN_H > IMG_STD_HEIGHT:
                print("The font size: %d is too big to print %s in one line" %(fontsize, item))
                sys.exit(-1)

        img = Image.new("1", (IMG_STD_HEIGHT, total_length), 'black')

        draw = ImageDraw.Draw(img)


        start_height = LABEL_C_MODE_MERGIN / 2;
        for item in text.split(" "):
            print(item)
            width , height = getSize(item, font)
            draw.text((( IMG_STD_HEIGHT - MARGIN_H -width ) / 2, MARGIN_V/2 + start_height), item, font = font, fill = 'white')
            start_height = start_height + height + LABEL_C_MODE_MERGIN
            draw.line([(0,start_height - LABEL_C_MODE_MERGIN /2 ), (5, start_height - LABEL_C_MODE_MERGIN /2 )],
                      fill = 'white', width = 0)

            draw.line([(IMG_STD_HEIGHT ,start_height - LABEL_C_MODE_MERGIN /2 ), (IMG_STD_HEIGHT - 5, start_height - LABEL_C_MODE_MERGIN /2 )],
                      fill = 'white', width = 0)

        img = img.rotate(90, expand=True)


    else:
        if not fontsize:
            fontsize = 10
            height = 10
            while height < IMG_STD_HEIGHT - MARGIN_V :
                font = ImageFont.truetype(fontfile, fontsize)
                width, height = getSize(text, font)
                fontsize  = fontsize + 1
        else:
            font = ImageFont.truetype(fontfile, fontsize)
            width, height = getSize(text, font)

        img_width = width + MARGIN_H
        img_height = height + MARGIN_V
        img = Image.new("1", (img_width, img_height), 'black')
        draw = ImageDraw.Draw(img)
        draw.text(( MARGIN_H / 2, MARGIN_V /2 ), text, font = font, fill = 'white')
    
    img = img.rotate(-90, expand=True)

    w, h = img.size
    padded = Image.new('1', (128, h))
    x, y = (128-w)//2, 0
    nw, nh = x+w, y+h
    padded.paste(img, (x, y, nw, nh))
    img = padded
    img = ImageOps.mirror(img)

    return img

