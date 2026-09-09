
def read_cosi_ts_detect(inputfile):
    f_file = open(inputfile)
    content_file = f_file.read().splitlines()

    measured_l=0
    measured_b=0
    error_coo=0
    maxumumTS=0
    for line_file in content_file:
        line_object=line_file.split()
        if line_object[0]=="Galactic" and line_object[1]=="coordinate":
            measured_l = float(line_object[5].split('=')[1].replace(",",""))
            measured_b = float(line_object[6].split('=')[1].replace(",",""))
        if line_object[0]=="Linear" and line_object[1]=="Size":
             error_coo=float(line_object[6])
        if line_object[0]=="Maximum" and line_object[1]=="TS=":
            maxumumTS=float(line_object[2])
    return measured_l,measured_b,error_coo,maxumumTS


def read_base_pipeline_params(namefile):
    t_scan_start_back=0
    t_scan_stop_back=0
    t_scan_start_source=0
    t_scan_stop_source=0
    external_trigger_file=""
    output_dir=""
    t_scan_delta=0
    threshold_TS=0
    file_anomaly_detection=""
    f_file = open(namefile)
    content_file = f_file.read().splitlines()
    for line_file in content_file:
        line_object=line_file.split()
        if line_object[0]=="t_scan_start_back":
            t_scan_start_back=int( line_object[1])
        if line_object[0]=="t_scan_stop_back":
            t_scan_stop_back=int( line_object[1])
        if line_object[0]=="t_scan_start_source":
            t_scan_start_source=int( line_object[1])
        if line_object[0]=="t_scan_stop_source":
            t_scan_stop_source=int( line_object[1])
        if line_object[0]=="t_scan_delta":
            t_scan_delta=int( line_object[1])
        if line_object[0]=="ExternalTrigger":
            external_trigger_file=str( line_object[1])
        if line_object[0]=="OutputDir":
            output_dir=str( line_object[1])
        if line_object[0]=="thresholdTS":
            threshold_TS=str( line_object[1])
        if line_object[0]=="AnomalyDetectionFile":
            file_anomaly_detection = str( line_object[1])
        
    return t_scan_start_source,t_scan_stop_source,t_scan_start_back,t_scan_stop_back,t_scan_delta,external_trigger_file,threshold_TS,output_dir,file_anomaly_detection

def read_trigger_content(contentname):
    externalTrigger_start=0
    externalTrigger_stop=0
    trigger_external=False
    f_file = open(contentname)
    content_file = f_file.read().splitlines()
    for line_trigger_tot in content_file:
        line_trigger=line_trigger_tot.split()
        print('********************** ',line_trigger[0])
        if line_trigger[0]=="timeStart":
            externalTrigger_start=int(line_trigger[1])
        if line_trigger[0]=="timeStop":
            externalTrigger_stop=int(line_trigger[1])
        if line_trigger[0]=="trigger_external":
            trigger_external=line_trigger[1]

    return externalTrigger_start,externalTrigger_stop,trigger_external

def read_trigger_content_multiple(filelistname):
    import torch

    f_file_list = open(filelistname)
    content_file_list = f_file_list.read().splitlines()
    ###
    numFiles_trigger = len(content_file_list)
    print(numFiles_trigger," trigger files detected")
    externalTrigger_start=torch.zeros(int(numFiles_trigger),dtype=torch.int64)
    externalTrigger_stop=torch.zeros(int(numFiles_trigger),dtype=torch.int64)
    trigger_external=numFiles_trigger
    ###
    file_test=0
    for line_file_name in content_file_list:        
        f_file = open(line_file_name)
        content_file = f_file.read().splitlines()
        for line_trigger_tot in content_file:
            line_trigger=line_trigger_tot.split()
            if line_trigger[0]=="timeStart":
                externalTrigger_start[file_test]=int(line_trigger[1])
                print('********************** ',line_trigger[0],line_trigger[1],int(line_trigger[1]))
            if line_trigger[0]=="timeStop":
                externalTrigger_stop[file_test]=int(line_trigger[1])
        file_test+=1
    print('++++++++++++++------- ',externalTrigger_start)
    return externalTrigger_start,externalTrigger_stop,numFiles_trigger

def count_trigger_num(filelistname):
    f_file_list = open(filelistname)
    content_file_list = f_file_list.read().splitlines()
    numFiles_trigger = len(content_file_list)
    print(numFiles_trigger," trigger files detected")
    return numFiles_trigger

def read_anomaly_detection_config(contentname):
    input_file_name=""
    model_file=""
    resolution_angle=0
    resolution_time=0
    plotting_window=0
    ori_file=""
    true_b=0
    true_l=0
    threshold_loss=0
    out_file=""
    f_file = open(contentname)
    content_file = f_file.read().splitlines()
    for line_trigger_tot in content_file:
        line_trigger=line_trigger_tot.split()
        if line_trigger[0]=="input_file":
            input_file_name=str(line_trigger[1])
        if line_trigger[0]=="model_file":
            model_file=str(line_trigger[1])
        if line_trigger[0]=="resolution_angle":
            resolution_angle=int(line_trigger[1])
        if line_trigger[0]== "resolution_time":
            resolution_time=int(line_trigger[1])
        if line_trigger[0]== "plotting_window":
            plotting_window=int(line_trigger[1])
        if line_trigger[0]== "orientation_file":
            ori_file=str(line_trigger[1])
        if line_trigger[0]== "true_position":
            true_b=float(line_trigger[1])
            true_l=float(line_trigger[2])
        if line_trigger[0]== "loss_threshold":
            threshold_loss=float(line_trigger[1])
        if line_trigger[0]== "file_out":
            out_file=str(line_trigger[1])
             
    return input_file_name,model_file,resolution_angle,resolution_time,plotting_window,ori_file,true_b,true_l,threshold_loss,out_file


def format_override_val(fitmodel,measured_l,measured_b,error_coo):
    modelname="zero"
    stringtooverride="zero"
    if fitmodel==0:
        modelname="pw"
        stringtooverride="model:template "
    if fitmodel==1:
        modelname="band"
        stringtooverride="model:template_grb "

    l_max= measured_l + 3.*error_coo  
    l_min= measured_l - 3.*error_coo
    b_max= measured_b + 3.*error_coo  
    b_min= measured_b - 3.*error_coo
    var_override1 = stringtooverride+"(point source):position:l:value=" + str(measured_l)
    var_override2 = stringtooverride+"(point source):position:b:value=" + str(measured_b)
    var_override3 = stringtooverride+"(point source):position:l:free=false"
    var_override4 = stringtooverride+"(point source):position:l:min_value=" + str(l_min)
    var_override5 = stringtooverride+"(point source):position:l:max_value=" +str(l_max)
    var_override6 = stringtooverride+"(point source):position:b:free=false"
    var_override7 = stringtooverride+"(point source):position:b:min_value=" + str(b_min)
    var_override8 = stringtooverride+"(point source):position:b:max_value=" + str(b_max)

    return var_override1,var_override2,var_override3,var_override4,var_override5,var_override6,var_override7,var_override8,modelname


def read_file_histo(data_full,startPoint,endPoint,resolutionImage_tmp,binNumTime_tmp,output_name,eventDuration,numEvt):
    import cosipy
    import torch
    from histpy import Histogram
    import healpy as hp
    import numpy as np
        
    imagePlotX_Z_t_tmp = torch.zeros(numEvt,resolutionImage_tmp,resolutionImage_tmp,resolutionImage_tmp,int(binNumTime_tmp))
    
    values = data_full.slice[{ "Time": slice(startPoint,endPoint) }].project("PsiChi","Phi","Time").contents
    histoPhi = data_full.slice[{ "Time": slice(startPoint,endPoint) }].project('Phi')
    histoTime = data_full.slice[{ "Time": slice(startPoint,endPoint) }].project('Time')
    
    f_out = open(output_name,"w")
    referenceBin=0
    for iii in range(histoTime.nbins):
        if iii%eventDuration==0:
            referenceBin=iii
        binTime = int(histoTime.axes['Time'].centers[iii].value - histoTime.axes['Time'].centers[referenceBin].value)             

        for i in range(data_full.project('PsiChi').nbins):
            Psi = hp.pix2ang(8, i)[0]
            Chi = hp.pix2ang(8, i)[1]
            binPsi = int(np.rad2deg(Psi) / 180. * resolutionImage_tmp)
            binChi = int(np.rad2deg(Chi) / 360. * resolutionImage_tmp)

            for ii in range(histoPhi.nbins):
                binPhi = int(histoPhi.axes['Phi'].centers[ii].value / 180. * resolutionImage_tmp)
                if values[i][ii][iii]>0:
                    imagePlotX_Z_t_tmp[int(iii/eventDuration)][binPsi][binChi][binPhi][binTime] += values[i][ii][iii]
                    print(int(iii/eventDuration),binPsi,binChi,binPhi,binTime,values[i][ii][iii],file=f_out)
        if iii%10==0:
            print(float(iii)/float(histoTime.nbins)*100,' % of data processed ')
    f_out.close()
    
    return imagePlotX_Z_t_tmp
    
def read_file_histo2(data_full,startPoint,endPoint,resolutionImage_tmp,binNumTime_tmp,output_name,eventDuration,numEvt):
    import cosipy
    import torch
    from histpy import Histogram
    import healpy as hp
    import numpy as np

    imagePlotX_Z_t_tmp = torch.zeros(numEvt,resolutionImage_tmp,2*resolutionImage_tmp,resolutionImage_tmp,int(binNumTime_tmp))
    
    values = data_full.slice[{ "Time": slice(startPoint,endPoint) }].project("PsiChi","Phi","Time").contents
    histoPhi = data_full.slice[{ "Time": slice(startPoint,endPoint) }].project('Phi')
    histoTime = data_full.slice[{ "Time": slice(startPoint,endPoint) }].project('Time')
    
    f_out = open(output_name,"w")
    referenceBin=0
    for iii in range(histoTime.nbins):
        if iii%eventDuration==0:
            referenceBin=iii
        binTime = int(histoTime.axes['Time'].centers[iii].value - histoTime.axes['Time'].centers[referenceBin].value)             

        for i in range(data_full.project('PsiChi').nbins):
            Psi = hp.pix2ang(8, i)[0]
            Chi = hp.pix2ang(8, i)[1]
            binPsi = int(np.rad2deg(Psi) / 180. * resolutionImage_tmp)
            binChi = int(np.rad2deg(Chi) / 360. * 2 * resolutionImage_tmp)

            for ii in range(histoPhi.nbins):
                binPhi = int(histoPhi.axes['Phi'].centers[ii].value / 180. * resolutionImage_tmp)
                if values[i][ii][iii]>0:
                    imagePlotX_Z_t_tmp[int(iii/eventDuration)][binPsi][binChi][binPhi][binTime] += values[i][ii][iii]
                    print(int(iii/eventDuration),binPsi,binChi,binPhi,binTime,values[i][ii][iii],file=f_out)
        if iii%10==0:
            print(float(iii)/float(histoTime.nbins)*100,' % of data processed ')
    f_out.close()
    
    return imagePlotX_Z_t_tmp


def read_spectral_fit_info(filetoprint,dir_plots,modeltoplot):
    """
    Read spectral fitting parameters from HDF5 result file.
    
    Parameters:
    - filetoprint: Index of the file to read (0, 1, 2, ...)
    - dir_plots: Directory containing HDF5 result files
    - modeltoplot: Model name to search for in filenames
    
    Returns:
    - NAME: Parameter names
    - VALUE: Best-fit parameter values
    - NEGATIVE_ERROR: Negative error bounds
    - POSITIVE_ERROR: Positive error bounds
    - UNIT: Units of parameters
    """

    from histpy import Histogram
    import os
    import re
    import h5py

    # Find all HDF5 files matching the model name in the directory
    nameFiles_fit = []
    for f in os.listdir(dir_plots):
        if f.lower().endswith(".h5") and str(modeltoplot) in f:
            fileName = os.path.join(dir_plots, f)
            nameFiles_fit.append(fileName)
            print(f)
            
    # Sort files by second-to-last number in filename (typically time value)
    nameFiles_fit_sorted = sorted(
        nameFiles_fit,
        key=lambda f: int(re.findall(r'\d+', f)[-2]) if len(re.findall(r'\d+', f)) >= 2 else 0
    )

    # Open the specified HDF5 file and read analysis results
    with h5py.File(nameFiles_fit_sorted[int(filetoprint)], "r") as f:
        data = f['AnalysisResults_0']    # Read analysis results dataset

        # Return the fitting parameters and their properties
        return data['NAME'][:],data['VALUE'][:],data['NEGATIVE_ERROR'][:],data['POSITIVE_ERROR'][:],data['UNIT'][:]

def read_file_histo_second(inputfilename,resolutionImage_tmp,binNumTime_tmp,numEvt):
    import torch
    from histpy import Histogram
    import healpy as hp
    import numpy as np

    imagePlotX_Z_t_tmp = torch.zeros(numEvt,resolutionImage_tmp,2*resolutionImage_tmp,resolutionImage_tmp,int(binNumTime_tmp))
    fileInput = open(inputfilename)
    content = fileInput.read().splitlines()
    for line in content:
        line2=line.split()
        numEvent=int(line2[0])
        binPsi = int(line2[1])
        binChi = int(line2[2])
        binPhi = int(line2[3])
        binTime = int(line2[4])
        value_save = float(line2[5])
        if value_save>0 and numEvent<numEvt: # and binTime>=maxevents[numEvent]-10 and binTime<maxevents[numEvent]+10:
            imagePlotX_Z_t_tmp[numEvent][binPsi][binChi][binPhi][binTime] += value_save
    return imagePlotX_Z_t_tmp


def read_trigger_content_multiple_yaml(lib_dir,filelistname):
    import sys
    sys.path.append(lib_dir)
    import torch
    from yayc import Configurator

    f_file_list = open(filelistname)
    content_file_list = f_file_list.read().splitlines()

    numFiles_trigger = len(content_file_list)
    print(numFiles_trigger," yaml trigger files detected")
    externalTrigger_start=torch.zeros(int(numFiles_trigger),dtype=torch.int64)
    externalTrigger_stop=torch.zeros(int(numFiles_trigger),dtype=torch.int64)
    trigger_external=numFiles_trigger
    
    file_test=0
    for line_file_name in content_file_list:        
        full_config = Configurator.open(str(line_file_name))
        t_start_source=full_config["external_trigger"]["t_external_start"]
        t_stop_source=full_config["external_trigger"]["t_external_stop"]
        lat_ext=full_config["external_trigger"]["lat_ext"]
        lon_ext=full_config["external_trigger"]["lon_ext"]
        externalTrigger_start[file_test]=int(t_start_source)
        externalTrigger_stop[file_test]=int(t_stop_source)
        file_test+=1
        
    print('++++++++++++++------- ',externalTrigger_start)
    return externalTrigger_start,externalTrigger_stop,numFiles_trigger
