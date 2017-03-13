#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sdxf
from utmll import LLtoUTM
import gi
try:
    gi.require_version('GExiv2', '0.10')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import GExiv2


def from_images_to_dxf(file_out, files):
    drawing = sdxf.Drawing()
    for afile in files:
        if os.path.exists(afile) and os.path.isfile(afile):
            filename = os.path.basename(afile)
            exif = GExiv2.Metadata(afile)
            coordinates = exif.get_gps_info()
            x, y, h = LLtoUTM(23, coordinates[1], coordinates[0])
            drawing.append(sdxf.Circle(center=(x, y, 0), radius=0.5, color=3))
            drawing.append(sdxf.Text(filename, point=(x, y, 0)))
    drawing.saveas(file_out)


if __name__ == '__main__':
    exif = GExiv2.Metadata('/home/lorenzo/Escritorio/IMG_20170228_125625.jpg')
    coordinates = exif.get_gps_info()
    print(coordinates)
    x, y, h = LLtoUTM(23, coordinates[1], coordinates[0])
    print(x, y)
    files = ['/home/lorenzo/Escritorio/IMG_20170228_125625.jpg']
    from_images_to_dxf('/home/lorenzo/Escritorio/ejemplo.dxf', files)
