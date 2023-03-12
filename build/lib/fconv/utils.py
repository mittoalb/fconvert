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


msg = """
	The script must be called in the directory where the edf to be converted are stored (example: Slices/)
	It creates automatically a subdirectory called 32bit/ or 16bit/ or 8bit/
	Specify output format (EDF,TIF,JP2) with: --out
	Specify output 32 or 16 or 8 bit with: --format
"""



def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 40):
	"""
	Print the progress bar in a loop - not for parallelized jobs
	"""
	filledLength    = int(round(barLength * iteration / float(total)))
	percents        = round(100.00 * (iteration / float(total)), decimals)
	bar             = '#' * filledLength + '-' * (barLength - filledLength)
	sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
	sys.stdout.flush()
	if iteration == total:
		print("\n")
		
		
class Counter(object):
	"""
	Implementation of a shared counter
	"""
	def __init__(self):
		self.val = mp.Value('i', 0)

	def increment(self, n=1):
		with self.val.get_lock():
			self.val.value += n
	@property
	def value(self):
		return self.val.value

import multiprocessing as mp
from contextlib import closing


def distribute_jobs(func,proj):
	"""
	Distribute a func over proj on different cores
	"""
	args = []
	pool_size = int(mp.cpu_count()/2)
	chunk_size = int((len(proj) - 1) / pool_size + 1)
	pool_size = int(len(proj) / chunk_size + 1)
	for m in range(pool_size):
		ind_start = int(m * chunk_size)
		ind_end = (m + 1) * chunk_size
		if ind_start >= int(len(proj)):
			break
		if ind_end > len(proj):
			ind_end = int(len(proj))
		args += [range(ind_start, ind_end)]
	with closing(mp.Pool(processes=pool_size)) as p:
		out = p.map_async(func, proj)
	out.get()
	p.close()		
	p.join()		


#def decoh_format(func):
def base_path():
	if form == "8":
		basedir = "./8bit/"
	elif form == "16":
		basedir = "./16bit/"
	elif form == "32":
		basedir = "./32bit/"
	return basedir

def format_convert(img,tmpA):
	if form == "16":
		img.data = display16bit(tmpA)
	elif form == "8":
		img.data = display8bit(tmpA)
	elif form == "32":
		pass
	else:
		print("Format not recognized")
		exit(0)
	return img.data

## 32 bit to 8 bit conversion
def display8bit(image): # copied from Bi Rico
	#image /= numpy.mean(image)
	display_min = numpy.min(numpy.min(image))
	display_max = numpy.max(numpy.max(image))
	image = numpy.array(image, copy=False)
	image.clip(display_min, display_max, out=image)
	image -= display_min
	image //= (display_max - display_min + 1) / 256.	
	return image.astype(numpy.uint8)

## 32 bit to 16 bit conversion
def display16bit(image): # copied from Bi Rico
	if ri[0] == 0 and ri[1] == 0:
	#image /= numpy.mean(image)
		display_min = numpy.min(numpy.min(image))
		display_max = numpy.max(numpy.max(image))
	else:
		display_min = ri[0]
		display_max = ri[1]
		numpy.clip(image,ri[0],ri[1])
	image = numpy.array(image, copy=False)
	image.clip(display_min, display_max, out=image)
	image -= display_min
	image //= (display_max - display_min + 1) / 16384.
	return image.astype(numpy.uint16)

def make_dir():
	path = "./"
	if args.format == "8":
		newpath=path + '8bit/'
		os.system('mkdir ' + newpath)
	elif args.format == "16":
		newpath=path + '16bit/'
		os.system('mkdir ' + newpath)
	elif args.format == "32":	
		newpath=path + '32bit/'
		os.system('mkdir ' + newpath)

def read_and_convert(i):
	img = fabio.open(filelist[i])
	img.rebin(binf,binf)

	img.header['Dim1'] = img.data.shape[0] 
	img.header['Dim2'] = img.data.shape[1]


	tmpA = numpy.zeros([img.data.shape[1],img.data.shape[0]])

	for n in range(0,binf):
		img = fabio.open(filelist[i+n])
		img.rebin(binf,binf)
		img.data += 1e-5
		img.data /= numpy.sum(img.data[0:10,0:10])
		tmpA[:,:] += img.data

	img.data = format_convert(img,tmpA)

	#update shared array
	slice_number =+ 1

	if out == "TIF":
		img = img.convert('tif')
		tmp = filelist[i].split(".edf")
		outname = base_path() + tmp[0][:-4] + str(int(i/binf)) + ".tif"
		img.save(outname)
	elif out == "EDF":
		outname = base_path() + filelist[i][:-8] + ".edf"
		img.save(outname)
	elif out == "JP2" and jp2f:
		outname = base_path() + tmp[0][:-4] + str(int(i/binf)) + ".jp2"
		jp2=glymur.Jp2k(outname, dataC)	
	else:
		print("Format not recognized")
		exit(0)
	
	printProgress(ct.value,Total/binf)
	ct.increment()
