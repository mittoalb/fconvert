#!/bin/pyhton
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SinoWID.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
  
__version__ = "0.1"
__author__ = "Alberto Mittone"
__lastrev__ = "Last revision: 11/03/23"

#Convert 32 bit edf images to 8 bit images
import os
import sys
import numpy
import string

from os import listdir
from os.path import isfile, join
import multiprocessing as mp
from multiprocessing import Pool
import argparse
import glob

import fabio
from utils import *


msg = """
	The script must be called in the directory where the edf to be converted are stored (example: Slices/)
	It creates automatically a subdirectory called 32bit/ or 16bit/ or 8bit/
	Specify output format (EDF,TIF,JP2) with: --out
	Specify output 32 or 16 or 8 bit with: --format
"""


#Read images convert and save 8bit
if __name__ == "__main__":


	import imp
	try:
		imp.find_module('glymur')
		found = True
	except ImportError:
		found = False
	
	if found:
		print("Jp2 conversion supported!")
		import glymur
	
	print(msg)

	parser = argparse.ArgumentParser(description='Format')
	parser.add_argument('--out', type=str, help='EDF of TIF or JP2',default='TIF')
	parser.add_argument('--format', type=str, help='32 or 16 of 8',default='16')
	parser.add_argument('--ri', type=str, help='Intensity range min:max',default='0:0')
	parser.add_argument('--binf', type=int, help='binning factor',default='2')
	
	#TO BE IMPLEMENTED AT CERTAIN POINT
	#parser.add_argument('--goc', type=str, help='Global or Cluster')
	args = parser.parse_args()
	
	
	#BAD PRACTICE MUST BE CHANGED
	global out
	global form
	global jp2f
	global binf	
	
	if args.ri:
		start, stop = [int(value) for value in args.ri.split(':')]
		ri = (start, stop)

	jp2f = found
	out = args.out
	form = args.format
	binf = args.binf

	
	#global totf	
	#DIRECTORY CREATION
	path = './'
	make_dir(args.form)
	
	#Initialize empty array
	global filelist
	filelist = []
	dirs = os.listdir( path )
	#Initialize counter
	ct = Counter()
	global Total
	Total = len(glob.glob('./*.edf'))

	print("I will process", Total, "number of files")
	for file in dirs:
		tmp = file.split('.edf')
		if len(tmp)==2:
			filelist = numpy.append(filelist, str(file))

	#Create shared array
	#Parallelization
	filelist.sort()

	proj=range(0,len(filelist)-1-binf,binf)
	slice_number = mp.Array('i',1)
	
	
	distribute_jobs(read_and_convert,proj)

	
