#!/usr/bin/env python

import os, sys, string, math
import netCDF4 as nc4
from datetime import datetime, timedelta
# import importlib

import gnome
from gnome.spill import point_line_release_spill
from gnome.outputters import Renderer, NetCDFOutput

from datetime import datetime, timedelta

from TAP_Setup import setup
from gnome.model import Model
from gnome.utilities.remote_data import get_datafile
from gnome.map import MapFromBNA

# from gnome.movers.py_current_movers import PyCurrentMover
# from gnome.movers.py_wind_movers import PyWindMover
from gnome.movers.random_movers import RandomMover
from gnome.environment import GridCurrent, GridWind
from gnome.movers import GridCurrentMover, GridWindMover
import gc

#from batch_gnome import batch_gnome

# create command file dir if it doesn't exist
print "RootDir is", setup.RootDir

def make_dir(name):
    path = os.path.join(setup.RootDir, name)
    if not os.path.exists(path):
        os.makedirs(path)

def make_model(base_dir='.'):
    #,images_dir=os.path.join(base_dir, 'images',gdat_dir='/data/dylan/ArcticTAP/data_gnome/ROMS_h2ouv/')):
    print 'initializing the model'
    print base_dir
    start_time = datetime(1985, 1, 1, 13, 31)
    # start with generic times...this will be changed when model is run
    model = Model(start_time=start_time,time_step=setup.time_step)

    mapfile = get_datafile(os.path.join(base_dir, setup.MapFileName))
    print mapfile
    print 'adding the map'
    model.map = MapFromBNA(mapfile, refloat_halflife=0.0)  # seconds

    return model

### CURRENT
# do some finagling with the start times in the data files
for ff in os.listdir(setup.Data_Dir):
    if ff.endswith("filelist.txt"):
        fn = ff

f = file(os.path.join(setup.Data_Dir,fn))
flist = []
for line in f:
    name = os.path.join(setup.Data_Dir, line)
    flist.append(name[:-1])   # Gonzo cat version
    # flist.append(name[:-1])   # laptop current version
Time_Map = []
for fn in flist:
    d = nc4.Dataset(fn)
    t = d['time']
    file_start_time = nc4.num2date(t[0], units=t.units)
    Time_Map.append( (file_start_time, fn) )

### WIND
# do some finagling with the start times in the data files
for ff in os.listdir(setup.Data_DirW):
    if ff.endswith("filelist.txt"):
        fn = ff
# fn = os.path.join(setup.Data_Dir,'SoCal_filelist.txt')
f = file(os.path.join(setup.Data_DirW,fn))
flist = []
for line in f:
    name = os.path.join(setup.Data_DirW, line)
    flist.append(name[:-1])   # Gonzo cat version
    # flist.append(name[:-1])   # laptop current version
Time_Map_W = []
for fn in flist:
    d = nc4.Dataset(fn)
    t = d['time']
    file_start_time = nc4.num2date(t[0], units=t.units)
    Time_Map_W.append( (file_start_time, fn) )




# load up the start positions
start_positions = open(os.path.join(setup.RootDir,
                                    setup.CubeStartSitesFilename)).readlines()
start_positions = [pos.split(',') for pos in start_positions]
start_positions = [( float(pos[0]), float(pos[1]) ) for pos in start_positions]

# model timing
release_duration = timedelta(hours=setup.ReleaseLength)
run_time = timedelta(hours=setup.TrajectoryRunLength)
# model.duration = run_time

NumStarts = setup.NumStarts


# # loop through seasons
for Season in setup.StartTimeFiles:
    SeasonName = Season[1]
    start_times = open(Season[0],'r').readlines()[:setup.NumStarts]
    #start_times = open(os.path.join(setup.RootDir, "All_yearStarts.txt")).readlines()

    make_dir(os.path.join(setup.RootDir,setup.TrajectoriesPath,SeasonName))
    print Season

    # get and parse start times in this season
    start_dt = []
    for start_time in start_times:
        start_time = [int(i) for i in start_time.split(',')]
        start_time = datetime(start_time[2],
                              start_time[1],
                              start_time[0],
                              start_time[3],
                              start_time[4],
                              )
        start_dt.append(start_time)


    # for time_idx, start_time in enumerate(start_dt):
    for time_idx in setup.RunStarts:
        gc.collect()    # Jay addition

        start_time = start_dt[time_idx]
        end_time = start_time + run_time
        print start_time, end_time  

        # # set up the model with the correct forcing files for this time/duration
        # file_list = []
        # i = 0
        # for i in range(0, len(Time_Map) - 1):
        #     curr_t, curr_fn = Time_Map[ i ]
        #     next_t, next_fn = Time_Map[ i+1 ]
        #     if next_t > start_time:
        #         file_list.append( curr_fn )
        #         if next_t > end_time:
        #             break
        # file_list.append( next_fn )    # pad the list with next file to cover special case of last file. 
        #                                 #   awkward. fix later
        # print 'number of ROMS files :: ', len(file_list)
        # print file_list
        
        # # set up the model with the correct forcing files for this time/duration
        # file_list_w = []
        # i = 0
        # for i in range(0, len(Time_Map_W) - 1):
        #     curr_t, curr_fn = Time_Map_W[ i ]
        #     next_t, next_fn = Time_Map_W[ i+1 ]
        #     if next_t > start_time:
        #         file_list_w.append( curr_fn )
        #         if next_t > end_time:
        #             break
        # file_list_w.append( next_fn )    # pad the list with next file to cover special case of last file. 
        #                                 #   awkward. fix later
        # print 'number of wind files :: ', len(file_list_w)
        # print file_list_w


        # set up model for this start_time/duration, adding required forcing files
        model = make_model(setup.RootDir)
        model.duration = run_time
        model.movers.clear()

        # print 'creating curr MFDataset'
        # ds_c = nc4.MFDataset(file_list)
        
        # print 'adding a CurrentMover (Trapeziod/RK4):'
        # g_curr = GridCurrent.from_netCDF(filename=file_list,
        #                                dataset=ds_c,
        #                                grid_topology={'node_lon':'lonc','node_lat':'latc'})
        # c_mover = PyCurrentMover(current=g_curr, default_num_method='Trapezoid')
        # model.movers += c_mover

        # print 'creating wind MFDataset'
        # ds_w = nc4.MFDataset(file_list_w)

        # print 'adding a WindMover (Euler):'
        # g_wind = GridWind.from_netCDF(filename=file_list_w,
        #                             dataset=ds_w,
        #                             grid_topology={'node_lon':'lonc','node_lat':'latc'})
        # w_mover = PyWindMover(wind = g_wind, default_num_method='Euler')
        # model.movers += w_mover
        


        print 'adding a CurrentMover (Trapeziod/RK4):'
        c_mover = GridCurrentMover(os.path.join(setup.Data_Dir,setup.CurrCatFile),
                                   os.path.join(setup.Data_Dir,setup.CurrTopoFile),
                                   num_method='RK4'
                                   )
        model.movers += c_mover


        print 'adding a WindMover (Euler):'
        w_mover = GridWindMover(os.path.join(setup.Data_DirW,setup.WindCatFile),
                                os.path.join(setup.Data_DirW,setup.WindTopoFile)
                                )
        model.movers += w_mover

        print 'adding a RandomMover:'
        model.movers += RandomMover(diffusion_coef=50000)




        # for pos_idx, start_position in enumerate(start_positions):
        for pos_idx in setup.RunSites:
            start_position = start_positions[pos_idx]

            OutDir = os.path.join(setup.RootDir,setup.TrajectoriesPath,SeasonName,'pos_%03i'%(pos_idx+1))
            make_dir(OutDir)

            print pos_idx, time_idx
            print "Running: start time:", start_time,
            print "At start location:",   start_position

            ## set the spill to the location
            # spill = point_line_release_spill(num_elements=setup.NumLEs,
            #                                  start_position=( start_position[0], start_position[1], 0.0 ),
            #                                  end_position=( start_position[0]+0.4, start_position[1]+0.2, 0.0 ),
            #                                  release_time=start_time,
            #                                  end_release_time=start_time+release_duration
            #                                  )
            spill = point_line_release_spill(num_elements=setup.NumLEs,
                                             start_position=( start_position[0], start_position[1], 0.0 ),
                                             release_time=start_time,
                                             end_release_time=start_time+release_duration
                                             )


            # set up the renderer location
            image_dir = os.path.join(setup.RootDir, 'Images',SeasonName, 'images_pos_%03i-time_%03i'%(pos_idx+1, time_idx))
            renderer = Renderer(os.path.join(setup.RootDir, setup.MapFileName),
                                image_dir,
                                image_size=(800, 600),
                                output_timestep=timedelta(hours=setup.out_delta))
            renderer.graticule.set_DMS(True)
            #renderer.viewport = ((-120.6666, 33.75),(-119.25, 34.5)) 
            make_dir(image_dir)

            # print "adding netcdf output"
            netcdf_output_file = os.path.join(OutDir,
                                              'pos_%03i-t%03i_%08i.nc'%(pos_idx+1, time_idx,
                                                int(start_time.strftime('%y%m%d%H'))),
                                              )


            model.start_time = start_time

            ## clear the old outputters
            model.outputters.clear()
            # model.outputters += renderer
            model.outputters += NetCDFOutput(netcdf_output_file,output_timestep=timedelta(hours=setup.out_delta))

            # clear out the old spills:
            model.spills.clear()
            model.spills+=spill

            model.full_run(rewind=True)
            # for i, step in enumerate(model):
            #      print i, step
            #      print
            #      for sc in model.spills.items():
            #          print "status_codes:", sc['status_codes']
            #          print "positions:", sc['positions']
            #          print "lw positions:", sc['last_water_positions']


