#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-

import os
import sdxf
from utmll import LLtoUTM
from xml.dom import minidom, Node

class GPXParser:
	def __init__(self, filename):
		try:
			doc = minidom.parse(filename)
			doc.normalize()
		except:
			return # handle this properly later
		self.gpx = doc.documentElement		
	def parse(self):
		points = []
		for wpt in self.gpx.getElementsByTagName('wpt'):
			lat = float(wpt.getAttribute('lat'))
			lon = float(wpt.getAttribute('lon'))
			if len(wpt.getElementsByTagName('ele'))>0:
				ele = float(wpt.getElementsByTagName('ele')[0].firstChild.data)
			else:
				ele = 0
			E,N,Z = LLtoUTM(23,lat,lon)
			points.append((E, N, ele))
		for trkpt in self.gpx.getElementsByTagName('trkpt'):
			lat = float(trkpt.getAttribute('lat'))
			lon = float(trkpt.getAttribute('lon'))
			ele = float(trkpt.getElementsByTagName('ele')[0].firstChild.data)
			E,N,Z = LLtoUTM(23,lat,lon)
			points.append((E, N, ele))
		return points


def from_gpx_to_dxf(afile):
	if os.path.exists(afile) and os.path.isfile(afile):
		head, tail = os.path.split(afile)
		root, ext = os.path.splitext(tail)
		file_out = os.path.join(head,root+'.dxf')
		#
		gpx_file = open(afile)
		gpx_parser = GPXParser(gpx_file)
		points = gpx_parser.parse()
		drawing = sdxf.Drawing()
		if len(points)>0:
			drawing.append(sdxf.PolyLine(points=points, color=1))	
		drawing.saveas(file_out)
		return True
	return False
		

if __name__ == '__main__':
	from_gpx_to_dxf('/home/atareao/Escritorio/fells_loop.gpx')
