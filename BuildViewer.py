#!/usr/bin/env python

"""
A simple script that copies all the cubes and everything into the right places

This has not been well set up to work universally. It's only been tested on one setup

"""
import os, shutil
from TAP_Setup import setup

TAPViewerDir = os.path.join(setup.RootDir, setup.TAPViewerPath)

#Check if TAP Viewer Dir exists:
if not os.path.isdir(TAPViewerDir):
    print "making new TAP Viewer Directory"
    os.mkdir(TAPViewerDir)

# copy the exe and settings files
shutil.copy(os.path.join(setup.RootDir, 'Tapfiles', 'TapView', 'TAP.exe'), TAPViewerDir)
shutil.copy(os.path.join(setup.RootDir, 'Tapfiles', 'TapView', 'SETTINGS.TAP'), TAPViewerDir)

# Check for TAPDATA
TAPDATADir = os.path.join(TAPViewerDir,"TAPDATA")
if not os.path.isdir(TAPDATADir):
    print "Making TAPDATA Directory"
    os.mkdir(TAPDATADir)

# copy the TAPCONFIG file
shutil.copy(os.path.join(setup.TAPViewerSource, "TAPCONFIG.txt"), TAPDATADir)

# copy the site.txt file
shutil.copy(os.path.join(setup.RootDir,"site.txt"), TAPDATADir)
shutil.copy(os.path.join(setup.TAPViewerSource, setup.MapFileName), TAPDATADir)

# copy the start times file (not required, but it's good to have it there
# print setup.StartTimeFiles
# for (filename, _) in setup.StartTimeFiles:
#     shutil.copy(filename, TAPDATADir)

FullCubesPath = os.path.join(setup.RootDir, setup.CubesPath) 

for (season, junk) in setup.Seasons:
    SeasonPath = os.path.join(TAPDATADir,season)
    if not os.path.isdir(SeasonPath):
        print "Creating:", SeasonPath
        os.mkdir(SeasonPath)
    SeasonCubesPath = os.path.join(FullCubesPath,season)
    print SeasonPath, SeasonCubesPath
    
    for name in os.listdir(SeasonCubesPath):
        print "Moving:", name
        shutil.move(os.path.join(SeasonCubesPath,name),
                     os.path.join(SeasonPath,name) )

# copy the script and Setup_TAP files to viewer dir for archive
setfile = os.path.join(setup.RootDir,'Setup_TAP.py')
shutil.copy(setfile, TAPViewerDir)

# shutil.copy(setup.PyGnome_script+'.py', TAPViewerDir)

# move Trajectories to TapViewer dir
# shutil.move(setup.TrajectoriesPath, TAPViewerDir)

