#!/usr/bin/env python
"""
A way to import a particular setup by only changing one thing
"""

# getting the root dir from the command line:

import sys, os
import datetime
import numpy as np

# get default paramaters
setup = __import__('Setup_TAP')




def getSetup():

	RootDir = os.path.abspath(__file__)

	if not os.path.exists(RootDir):	
		raise Exception("RootDir: %s Doesn't exist"%RootDir)

	sys.path.insert(0, RootDir)	
	setup = __import__('Setup_TAP')
	setup.RootDir = RootDir

	print setup

	return setup


def paramstest():

	class pp:
		pass
	# number of start times you want in each season:
	pp.NumStarts = 500

	# # Length of release in hours  (0 for instantaneous)
	pp.ReleaseLength = 30 *24  # in hours

	# name of the GNOME script file to run
	pp.PyGnome_script = "script_ArcticTAP"

	# number of Lagrangian elements you want in the GNOME run
	pp.NumLEs = 1000
	return pp

