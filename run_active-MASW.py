"""
Author : José CUNHA TEIXEIRA
License : SNCF Réseau, UMR 7619 METIS
Date : November 30, 2023
"""

import numpy as np
from obspy import read
from os import path, mkdir
from obspy2numpy import stream_to_array
from misc import diag_print
from display import display_spectrum_img_fromArray, display_dispersion_img, display_seismic_wiggle_fromStream
from folders import results_dir, data_dir
from slant_stack import slant_stack
from signal_processing import makeFV



profile = "P2" #Profile number
data_dir = f"{data_dir}/" + profile + "/Active/"
if not path.exists(results_dir):
    mkdir(results_dir)
results_dir = f"{results_dir}/" + profile 
if not path.exists(results_dir):
    mkdir(results_dir)
results_dir = f"{results_dir}/" + "Active/"
if not path.exists(results_dir):
    mkdir(results_dir)

files = [profile[1:] + "001", profile[1:] + "002"]
x_sources = [-0.125, 23.875]

N_sensors = 96

x_sensors = np.arange(0.0, 24, 0.25)

W_MASW = 96
starts_MASW = [0, 0]
display_method = "save"
fmin = 0
fmax = 200
dv = 0.1
vmin = 1
vmax = 2000
shot_length_cut = None


for file, x_source, start_MASW in zip(files, x_sources, starts_MASW) :

    diag_print("Info", "Main", f"Processing {file}")
    st = read(f'{data_dir}' + file + ".dat")

    if display_method == "save" and not path.exists(f'{results_dir}' + file + "/"):
        mkdir(f"{results_dir}" + file + "/")

    if display_method == "save" and not path.exists(f'{results_dir}' + file + "/" + f"W{W_MASW}/"):
        mkdir(f'{results_dir}' + file + "/" + f"W{W_MASW}/")


    ### TIME AND FREQUENCY PARAMETERS ------------------------------------
    Nt = st[0].stats.npts
    dt = st[0].stats.delta
    ts = np.arange(0, (Nt*dt), dt)
    Nx = len(st)
    f_ech = st[0].stats.sampling_rate

    print(f"Number of samples : {Nt}")
    print(f"Time step : {dt} s")
    print(f"Record length : {ts[-1]} s")
    print(f"Number of traces : {Nx}")
    print(f"Sampling rate : {f_ech} Hz")


    ### DATA ARRAY -------------------------------------------------------
    data_array = stream_to_array(st, len(st), Nt)

    if shot_length_cut != None and shot_length_cut <= Nt*dt:
        print(f"Cutting wiggle at {shot_length_cut} s")
        data_array_cut = np.zeros((int(shot_length_cut/dt), data_array.shape[1]))
        for i, tr in enumerate(data_array.T):
            data_array_cut[:, i] = tr[0:int(shot_length_cut/dt)]
        data_array = data_array_cut

    ### WIGGLE -----------------------------------------------
    name_path = f'{results_dir}' + file + "/" + f"W{W_MASW}/" + f"{file}_wiggle.png"
    display_seismic_wiggle_fromStream(st, x_sensors, display_method=display_method, path=name_path, norm_method="trace")


    ### SPECTROGRAM ------------------------------------------------------
    name_path1 = f'{results_dir}' + file + "/" + f"W{W_MASW}/" + f"{file}_spectrogram.png"
    name_path2 = f'{results_dir}' + file + "/" + f"W{W_MASW}/" + f"{file}_spectrogramFirstLastTrace.png"
    display_spectrum_img_fromArray(data_array, dt, x_sensors, display_method=display_method, path1=name_path1, path2=name_path2, norm_method="trace")


    ## SLANT STACK ------------------------------------------------------
    offsets = np.abs(x_sensors - x_source)
    (FV, vs, fs) = slant_stack(data_array.T[start_MASW:start_MASW+W_MASW,:], dt, offsets[start_MASW:start_MASW+W_MASW], vmin, vmax, dv, fmax)
    name_path = f'{results_dir}' + file + "/" + f"W{W_MASW}/" + f"{file}_dispIm.png"
    display_dispersion_img(FV, fs, vs, display_method=display_method, path=name_path, normalization="Frequency")

    np.save(f'{results_dir}' + file + "/" + f"W{W_MASW}/" + f"{file}_dispIm.npy", FV)
    np.save(f'{results_dir}' + file + "/" + f"W{W_MASW}/" + f'{file}_fs.npy', fs)
    np.save(f'{results_dir}' + file + "/" + f"W{W_MASW}/" + f'{file}_vs.npy', vs)
