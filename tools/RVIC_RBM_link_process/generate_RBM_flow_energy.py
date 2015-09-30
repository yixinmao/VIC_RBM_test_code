#!/usr/local/anaconda/bin/python

# This script

import numpy as np
import sys
import datetime as dt
import pandas as pd
import xray
import my_functions

cfg = my_functions.read_config(sys.argv[1])  # Read config file

#====================================================#
# Parameter loading from config file
#====================================================#
# [INPUT]
# Routing station file - output from 'prepare_RBM_param.py'
route_station_file = cfg['INPUT']['route_station_file']
# VIC output nc file - flow
vic_output_flow_nc = cfg['INPUT']['vic_output_flow_nc']
# VIC output nc file - energy
vic_output_energy_nc = cfg['INPUT']['vic_output_energy_nc']
# VIC output time step - flow (units: hour)
vic_flow_dt = cfg['INPUT']['vic_flow_dt']
vic_energy_dt = cfg['INPUT']['vic_energy_dt']

# [RBM_OPTIONS]
# RBM start and end date
start_date = dt.date(cfg['RBM_OPTIONS']['start_date'][0], \
                         cfg['RBM_OPTIONS']['start_date'][1], \
                         cfg['RBM_OPTIONS']['start_date'][2])
end_date = dt.date(cfg['RBM_OPTIONS']['end_date'][0], \
                         cfg['RBM_OPTIONS']['end_date'][1], \
                         cfg['RBM_OPTIONS']['end_date'][2])

#====================================================#
# Load latlon list for flow and energy grid cells
#====================================================#
print 'Loading routing station file...'
f = open(route_station_file, 'r')
#=== Read first line (# flow cells; # energy cells) ===#
line = f.readline().rstrip("\n")
n_flow = int(line.split()[0])
n_energy = int(line.split()[1])
#=== Loop over each flow/energy grid cell ==#
list_flow_lat_lon = []  # list of flow cells ([lat, lon])
list_energy_lat_lon = []  # list of energy cells ([lat, lon])
while 1:
    line = f.readline().rstrip("\n")
    if line=="":
        break
    if line.split()[0]=="1":  # if this is a flow cell (i.e., not the end of a reach)
        lat_lon = line.split()[2]
        list_flow_lat_lon.append([float(lat_lon.split('_')[0]), \
                                  float(lat_lon.split('_')[1])])
        list_energy_lat_lon.append([float(lat_lon.split('_')[0]), \
                                    float(lat_lon.split('_')[1])])
        line = f.readline().rstrip("\n")  # Read the next line - None or path for uh_s file
    elif line.split()[0]=="0":  # if this is NOT a flow cell (i.e., the end of a reach)
                                # Only energy grid cell
        lat_lon = line.split()[2]
        list_energy_lat_lon.append([float(lat_lon.split('_')[0]), \
                                    float(lat_lon.split('_')[1])])
#=== Check whether the number of flow/energy cells are correct ===#
if len(list_flow_lat_lon)!=n_flow or len(list_energy_lat_lon)!=n_energy:
    print 'Error: incorrect number of flow/energy cells!'
    exit()

#====================================================#
# Load VIC output data - energy
#====================================================#
print 'Loading and processing VIC output energy data...'

vic_energy_daily = {}  # keys: energy veriables; content: xray.DataArray of daily data

#=== Load data ===#
ds_vic_energy = xray.open_dataset(vic_output_energy_nc)

#=== If sub-daily data, convert to daily ===#
print 'Converting sub-daily to daily data...'
for var in ['Tair', 'vp', 'Shortwave', 'Longwave', 'Density', 'Pressure', 'Wind']:
    if vic_energy_dt<24:
        vic_energy_daily[var] = ds_vic_energy[cfg['INPUT'][var]]\
                                .groupby('time.date').mean(dim='time')
    elif vic_energy_dt==24:
        vic_energy_daily[var] = ds_vic_energy[cfg['INPUT'][var]]
    else:
         print 'Error: VIC energy output time interval must be 24 or less hours!'

#=== Select time range for RBM ===#
print 'Selecting time range...'
for var in ['Tair', 'vp', 'Shortwave', 'Longwave', 'Density', 'Pressure', 'Wind']:
    vic_energy_daily[var] = vic_energy_daily[var].loc[start_date:end_date, :, :]

#=== Converting units ===#
print 'Converting units...'
vic_energy_daily['vp'] = vic_energy_daily['vp'] * 10.0 # convert [kPa] to [mb]
vic_energy_daily['Shortwave'] = vic_energy_daily['Shortwave'] \
                                * 2.388 * np.power(10, -4) # convert [W/m2] to [mm*K/s]
vic_energy_daily['Longwave'] = vic_energy_daily['Longwave'] \
                               * 2.388 * np.power(10, -4) # convert [W/m2] to [mm*K/s]
vic_energy_daily['Pressure'] = vic_energy_daily['Pressure'] * 10.0 # convert [kPa] to [mb]

#====================================================#
# Writing data to file
#====================================================#
#=== Write energy data ===#
f = open(cfg['OUTPUT']['rbm_energy_file'], 'w')
for i, date in enumerate(vic_energy_daily['Tair'].coords['date']):
    print 'Writing energy data to file, day {}...'.format(i+1)
    for j, lat_lon in enumerate(list_energy_lat_lon):
        lat = lat_lon[0]
        lon = lat_lon[1]
        f.write('{:d} {:.1f} {:.1f} {:.4f} {:.4f} {:.3f} {:.1f} {:.1f}\n'\
                .format(j+1, float(vic_energy_daily['Tair'].loc[date, lat, lon].values), \
                        float(vic_energy_daily['vp'].loc[date, lat, lon].values), \
                        float(vic_energy_daily['Shortwave'].loc[date, lat, lon].values), \
                        float(vic_energy_daily['Longwave'].loc[date, lat, lon].values), \
                        float(vic_energy_daily['Density'].loc[date, lat, lon].values), \
                        float(vic_energy_daily['Pressure'].loc[date, lat, lon].values), \
                        float(vic_energy_daily['Wind'].loc[date, lat, lon].values)))



