#!/usr/bin/env python

"""
TAPII.py

A program to simulate TAP II with Batch GNOME

This version will use either:
1) tradition TAP receptor sites
2) the Grided Receptors approach.
3) the Gridded average thickness approach.
depending on what is specified in TAP_Setup.py

It  builds TAP cubes out of a set of  trajectory files that resulting from a Batch GNOME run.

Input required:
- Setup_TAP.py file 
- a set of TAP trajectory files, generated by GNOME in Batch mode.
"""


#import sys
import os

import numpy as np
from time import time
import os, glob

# read the Setup_TAP.py file
from TAP_Setup import setup
from batch_gnome import tap_mod, batch_gnome, oil_weathering


print "\n--- Running Build cubes ---"


# create the dir for all the cubes:
FullCubesPath = os.path.join(setup.RootDir,setup.CubesPath) 
if not os.path.isdir(FullCubesPath):
    os.mkdir(FullCubesPath)

# Build list of Trajectory dirs and cube names:
CubesList = []
for ( (Season,Months), CubeRootName ) in zip(setup.Seasons, setup.CubesRootNames):
    # build the directory structure
    SeasonTrajDir = os.path.join(setup.RootDir, setup.TrajectoriesPath, Season)  #DDR
    # SeasonTrajDir = os.path.join(setup.RootDir, setup.TrajectoriesPath)
    SeasonCubesDir = os.path.join(setup.RootDir, setup.CubesPath, Season)
    if not os.path.isdir(SeasonCubesDir):
        print "Creating directory: ", SeasonCubesDir
        os.mkdir(SeasonCubesDir)

    DirList = os.listdir(SeasonTrajDir)
    DirList.sort()

    for d in DirList:
        try:
            int(d[4:7])
            GoOn = True
        except ValueError:
            GoOn = False
        if GoOn:
            TrajName = os.path.join(setup.RootDir,setup.TrajectoriesPath,Season,d)
            CubeName = os.path.join(setup.RootDir, setup.CubesPath, Season, "%s%s%s"%(CubeRootName, d[4:7].zfill(4),".bin") )
            CubesList.append((TrajName, CubeName, Months))
    print len(CubesList)


            
if setup.ReceptorType == "Grid":
    Grid = setup.Grid
    
    Receptors = tap_mod.Grid(Grid.min_long,
                             Grid.max_long,
                             Grid.min_lat,
                             Grid.max_lat,
                             Grid.num_lat,
                             Grid.num_long)
    
    for TrajFilesDir, CubeName, Months in CubesList:
        print 
        print "processing Cube::", CubeName 
        if not os.path.isdir(TrajFilesDir):
            raise Exception(TrajFilesDir + " is not a valid directory")
        ## if the file exists and it is non-empty it will be skipped
        CubeExists = os.path.isfile(CubeName)
        if CubeExists and ( os.path.getsize(CubeName) > 0 ): 
            print "Cube: %s Exists...skipping"%(CubeName,)

        elif CubeExists and (((time() - os.path.getmtime(CubeName)) / 60) < 30 ):
            print "EmptyCube: %s Exists less than 30min old...skipping"%(CubeName,)

        else:
            print "Compute Cube: %s \n from trajectory files in:\n %s"%(CubeName,TrajFilesDir)
            # TrajFiles = [os.path.join(TrajFilesDir, "time%03i.nc"%(i+1)) for i in range(setup.NumStarts)]

            TrajFiles = [os.path.join(TrajFilesDir,i) for i in os.listdir(TrajFilesDir)]
            
            # filter TrajFiles list
            # if setup.CubeStartFilter:
            tmnth = [int(i[-9:-7]) for i in TrajFiles]
            nmnth = np.asarray(tmnth)
            tt = np.where(np.in1d(nmnth,Months))
            tlist = []
            for i in tt[0]:
                tlist.append(TrajFiles[i])
            TrajFiles = tlist

            # # kludge fix to pad length of seasonal traj files to total NumStarts
            # # if len(TrajFiles < setup.NumStarts):
            # if len(TrajFiles) < 500:
            #     tlist = TrajFiles[0:250]
            #     for i in TrajFiles[0:250]:  
            #         tlist.append(i)
            # TrajFiles = tlist


            # make sure they exist
            ## fixme: should I check file size, too.
            for f in TrajFiles:
                if not os.path.exists(f):
                    raise Exception( "trajectory file missing: %s"%f )
                 
            # print "trajectory files are all there..."
            print "# of files :: %s" %(str(len(TrajFiles)))
            print "there are %i trajectory files"%len(TrajFiles)
            print "The first 5 are:"
            for name in TrajFiles[:5]:
               print name
            start = time()
            
            if not os.path.isdir(os.path.split(CubeName)[0]):
                os.mkdir(os.path.split(CubeName)[0])

            if setup.CubeType == "Cumulative":
                if setup.OilWeatheringType is not None:
                    raise NotImplimentedError("weathering not implimented for cumulative cubes")
                print "computing cumulative cubes"
                Cube = tap_mod.CompTAPIICube(TrajFiles,
                                             setup.OutputTimes,
                                             Receptors,
                                             oil_weathering.OilTypes[setup.OilWeatheringType])
            elif setup.CubeType == "Volume":
                print "computing volume cubes"
                Cube = tap_mod.CompThicknessCube(TrajFiles,
                                                 setup.OutputTimes,
                                                 Receptors,
                                                 oil_weathering.OilTypes[setup.OilWeatheringType])
                types = {'float32': np.float32,
                         'uint8'  : np.uint8,
                         'uint16' : np.uint16,
                         }
                try:
                    Cube = tap_mod.transform(Cube, setup.NumLEs, n = 1.5, dtype=types[setup.CubeDataType])
                except KeyError:
                    raise ValueError("Unsupported Cube Data Type: %s"%CubeDataType)
            
        
            #print " The Cube Shape is: %s"%(Cube.shape,)
            #print "The cube is %i elements, each one %i bytes"%(np.product(Cube.shape), Cube.itemsize())
            print "Computing the whole cube took %f seconds (%f minutes)"%((time()- start),(time()- start)/60)

            # write it out to a file:
            print "writing out cube:",CubeName
            #CubeFile = open(CubeName,'wb')
            #CubeFile.write(Cube.tostring())
            #CubeFile.close()
            Cube.tofile(CubeName)
else:
    print "Receptortype" , Receptortype, " isn't implimented yet"
