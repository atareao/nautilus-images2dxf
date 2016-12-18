#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-
#
__author__='atareao'
__date__ ='$11/02/2011'
#
# A library convert from/to utm to/from longitude/latitude
#
# Copyright (C) 2011 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
import math

PI = math.pi
FOURTHPI = PI / 4;
deg2rad = PI / 180;
rad2deg = 180.0 / PI;

Ellipsoid = []
#id, Ellipsoid name, Equatorial Radius, square of eccentricity	

Ellipsoid.append({'id':-1, 'name':'Placeholder','equatorial_radius':0,'eccentricity_squared':0})
Ellipsoid.append({'id': 1, 'name':'Airy','equatorial_radius':6377563,'eccentricity_squared':0.00667054})
Ellipsoid.append({'id': 2, 'name':'Australian National','equatorial_radius':6378160,'eccentricity_squared':0.006694542})
Ellipsoid.append({'id': 3, 'name':'Bessel 1841','equatorial_radius':6377397,'eccentricity_squared':0.006674372})
Ellipsoid.append({'id': 4, 'name':'Bessel 1841 (Nambia)' ,'equatorial_radius':6377484,'eccentricity_squared':0.006674372})
Ellipsoid.append({'id': 5, 'name':'Clarke 1866','equatorial_radius':6378206,'eccentricity_squared':0.006768658})
Ellipsoid.append({'id': 6, 'name':'Clarke 1880','equatorial_radius':6378249,'eccentricity_squared':0.006803511})
Ellipsoid.append({'id': 7, 'name':'Everest','equatorial_radius':6377276,'eccentricity_squared':0.006637847})
Ellipsoid.append({'id': 8, 'name':'Fischer 1960 (Mercury)' ,'equatorial_radius':6378166,'eccentricity_squared':0.006693422})
Ellipsoid.append({'id': 9, 'name':'Fischer 1968','equatorial_radius':6378150,'eccentricity_squared':0.006693422})
Ellipsoid.append({'id': 10, 'name':'GRS 1967','equatorial_radius':6378160,'eccentricity_squared':0.006694605})
Ellipsoid.append({'id': 11, 'name':'GRS 1980','equatorial_radius':6378137,'eccentricity_squared':0.00669438})
Ellipsoid.append({'id': 12, 'name':'Helmert 1906','equatorial_radius':6378200,'eccentricity_squared':0.006693422})
Ellipsoid.append({'id': 13, 'name':'Hough','equatorial_radius':6378270,'eccentricity_squared':0.00672267})
Ellipsoid.append({'id': 14, 'name':'International','equatorial_radius':6378388,'eccentricity_squared':0.00672267})
Ellipsoid.append({'id': 15, 'name':'Krassovsky','equatorial_radius':6378245,'eccentricity_squared':0.006693422})
Ellipsoid.append({'id': 16, 'name':'Modified Airy','equatorial_radius':6377340,'eccentricity_squared':0.00667054})
Ellipsoid.append({'id': 17, 'name':'Modified Everest','equatorial_radius':6377304,'eccentricity_squared':0.006637847})
Ellipsoid.append({'id': 18, 'name':'Modified Fischer 1960','equatorial_radius':6378155,'eccentricity_squared':0.006693422})
Ellipsoid.append({'id': 19, 'name':'South American 1969','equatorial_radius':6378160,'eccentricity_squared':0.006694542})
Ellipsoid.append({'id': 20, 'name':'WGS 60','equatorial_radius':6378165,'eccentricity_squared':0.006693422})
Ellipsoid.append({'id': 21, 'name':'WGS 66','equatorial_radius':6378145,'eccentricity_squared':0.006694542})
Ellipsoid.append({'id': 22, 'name':'WGS-72','equatorial_radius':6378135,'eccentricity_squared':0.006694318})
Ellipsoid.append({'id': 23, 'name':'WGS-84','equatorial_radius':6378137,'eccentricity_squared':0.00669438})



def LLtoUTM(ellipsoid, lat, lon):
	a = Ellipsoid[ellipsoid]['equatorial_radius']
	eccSquared = Ellipsoid[ellipsoid]['eccentricity_squared']
	k0 = 0.9996;
	LongOrigin = 0.0
	eccPrimeSquared = 0.0
	N = 0.0
	T = 0.0
	C = 0.0
	A = 0.0
	M = 0.0
	LongTemp = (lon+180)-int((lon+180)/360)*360-180#; // -180.00 .. 179.9;
	LatRad = lat*deg2rad
	LongRad = LongTemp*deg2rad
	ZoneNumber = Huso(lat,lon)
	LongOrigin = (ZoneNumber - 1)*6 - 180 + 3#+3 puts origin in middle of zone
	LongOriginRad = LongOrigin * deg2rad
	#compute the UTM Zone from the latitude and longitude
	#sprintf(UTMZone, "%d%c", ZoneNumber, UTMLetterDesignator(Lat));
	eccPrimeSquared = (eccSquared)/(1-eccSquared)
	N = a/math.sqrt(1-eccSquared*math.sin(LatRad)*math.sin(LatRad))
	T = math.tan(LatRad)*math.tan(LatRad)
	C = eccPrimeSquared*math.cos(LatRad)*math.cos(LatRad)
	A = math.cos(LatRad)*(LongRad-LongOriginRad)
	M = a*((1-eccSquared/4-3*math.pow(eccSquared,2)/64-5*math.pow(eccSquared,3)/256)*LatRad-(3*eccSquared/8+3*math.pow(eccSquared,2)/32+45*math.pow(eccSquared,3)/1024)*math.sin(2*LatRad)+(15*math.pow(eccSquared,2)/256+45*math.pow(eccSquared,3)/1024)*math.sin(4*LatRad)-(35*math.pow(eccSquared,3)/3072)*math.sin(6*LatRad))
	UTMEasting = k0*N*(A+(1-T+C)*math.pow(A,3)/6 + (5-18*T+math.pow(T,2)+72*C-58*eccPrimeSquared)*math.pow(A,5)/120)+500000.0
	UTMNorthing = k0*(M+N*math.tan(LatRad)*(math.pow(A,2)/2+(5-T+9*C+4*math.pow(C,2))*math.pow(A,4)/24 + (61-58*T+math.pow(T,2)+600*C-330*eccPrimeSquared)*math.pow(A,6)/720))
	if lat < 0:
		UTMNorthing += 10000000.0#10000000 meter offset for southern hemisphere
	return UTMEasting, UTMNorthing, str(ZoneNumber)+Banda(lat)
	
	
def Huso(latitud,longitud):
	LongTemp = (longitud+180)-int((longitud+180)/360)*360-180#; // -180.00 .. 179.9;
	huso = int((LongTemp + 180)/6) + 1
	if latitud >= 56.0 and latitud < 64.0 and LongTemp >= 3.0 and LongTemp < 12.0:
		huso = 32
	#Special zones for Svalbard
	if latitud >= 72.0 and latitud < 84.0:
		if LongTemp >= 0.0  and LongTemp <  9.0:
			huso = 31
		elif LongTemp >= 9.0 and LongTemp < 21.0:
			huso = 33
		elif LongTemp >= 21.0 and LongTemp < 33.0:
			huso = 35
		elif LongTemp >= 33.0 and LongTemp < 42.0:
			huso = 37
	return huso

	
def Banda(lat):
	letter = 'Z'
	if 84 >= lat and lat >= 72:
		letter = 'X'
	elif 72 > lat and lat >= 64:
		letter = 'W'
	elif 64 > lat and lat >= 56:
		letter = 'V'
	elif 56 > lat and lat >= 48:
		letter = 'U'
	elif 48 > lat and lat >= 40:
		letter = 'T'
	elif 40 > lat and lat >= 32:
		letter = 'S'
	elif 32 > lat and lat >= 24:
		letter = 'R'
	elif 24 > lat and lat >= 16:
		letter = 'Q'
	elif 16 > lat and lat >= 8:
		letter = 'P'
	elif 8 > lat and lat >= 0:
		letter = 'N'
	elif 0 > lat and lat >= -8:
		letter = 'M'
	elif-8> lat and lat >= -16:
		letter = 'L'
	elif-16 > lat and lat >= -24:
		letter = 'K'
	elif-24 > lat and lat >= -32:
		letter = 'J'
	elif-32 > lat and lat >= -40:
		letter = 'H'
	elif-40 > lat and lat >= -48:
		letter = 'G'
	elif-48 > lat and lat >= -56:
		letter = 'F'
	elif-56 > lat and lat >= -64:
		letter = 'E'
	elif-64 > lat and lat >= -72:
		letter = 'D'
	elif-72 > lat and lat >= -80:
		letter = 'C'
	return letter
	
#print LLtoUTM(23,39.36,-0.41)
#print UTMLetter(39.36)

def UTMtoLL(ellipsoid, UTMEasting, UTMNorthing, UTMZone):
	k0 = 0.9996
	a = Ellipsoid[ellipsoid]['equatorial_radius']
	eccSquared = Ellipsoid[ellipsoid]['eccentricity_squared']
	eccPrimeSquared = 0.0
	e1 = (1-math.sqrt(1-eccSquared))/(1+math.sqrt(1-eccSquared))
	N1 = 0.0
	T1 = 0.0
	C1 = 0.0
	R1 = 0.0
	D = 0.0
	M = 0.0
	LongOrigin = 0.0
	mu = 0.0
	phi1 = 0.0
	phi1Rad = 0.0
	x = 0.0
	y = 0.0
	ZoneNumber = 0
	NorthernHemisphere = 1 # 1 for northern hemispher, 0 for southern
	x = UTMEasting - 500000.0 #remove 500,000 meter offset for longitude
	y = UTMNorthing
	ZoneNumber=int(UTMZone[0:(len(UTMZone)-1)])
	ZoneLetter=UTMZone[(len(UTMZone)-1):]
	if (ord(ZoneLetter.upper()) - ord('N')) >= 0:
		NorthernHemisphere = 1 # point is in northern hemisphere
	else:
		NorthernHemisphere = 0 # point is in southern hemisphere
		y -= 10000000.0 # remove 10,000,000 meter offset used for southern hemisphere
	print(ZoneNumber, ZoneLetter, NorthernHemisphere)
	LongOrigin = (ZoneNumber - 1)*6 - 180 + 3#;  //+3 puts origin in middle of zone
	eccPrimeSquared = (eccSquared)/(1-eccSquared)
	M = y / k0
	mu = M/(a*(1-eccSquared/4-3*eccSquared*eccSquared/64-5*eccSquared*eccSquared*eccSquared/256))
	phi1Rad = mu+(3*e1/2-27*math.pow(e1,3)/32)*math.sin(2*mu)+(21*math.pow(e1,2)/16-55*math.pow(e1,4)/32)*math.sin(4*mu)+(151*math.pow(e1,3)/96)*math.sin(6*mu)
	phi1 = phi1Rad*rad2deg
	N1 = a/math.sqrt(1-eccSquared*math.sin(phi1Rad)*math.sin(phi1Rad))
	T1 = math.tan(phi1Rad)*math.tan(phi1Rad)
	C1 = eccPrimeSquared*math.cos(phi1Rad)*math.cos(phi1Rad)
	R1 = a*(1-eccSquared)/math.pow(1-eccSquared*math.sin(phi1Rad)*math.sin(phi1Rad), 1.5)
	D = x/(N1*k0);
	Lat = phi1Rad - (N1*math.tan(phi1Rad)/R1)*(math.pow(D,2)/2-(5+3*T1+10*C1-4*math.pow(C1,2)-9*eccPrimeSquared)*math.pow(D,4)/24+(61+90*T1+298*C1+45*math.pow(T1,2)-252*eccPrimeSquared-3*math.pow(C1,2))*math.pow(D,6)/720)
	Lat = Lat * rad2deg
	Long = (D-(1+2*T1+C1)*math.pow(D,3)/6+(5-2*C1+28*T1-3*math.pow(C1,2)+8*eccPrimeSquared+24*T1*T1)*math.pow(D,5)/120)/math.cos(phi1Rad)
	Long = LongOrigin + Long * rad2deg
	return Lat,Long
if __name__ == '__main__':
	E,N,Z = LLtoUTM (23,0,40)
	print(E,N,Z)
	exit(0)
