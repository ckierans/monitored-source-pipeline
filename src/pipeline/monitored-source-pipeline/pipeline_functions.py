import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import subprocess
import time
import warnings
import yaml
from typing import Any

from matplotlib.lines import Line2D

EXTERNAL_PYTHON = "/home/gamma/envs/cosipy_laura/bin/python"


def execute_bindata_crab(cosipy_yaml_input, lib_dir):
    import cosipy
    from cosipy.pipeline.task.task import cosi_bindata
    import subprocess
    from yayc import Configurator
    print('Binning source')

    full_config = Configurator.open(cosipy_yaml_input)
    tstart = full_config["general_pipeline_config"]["tstart"]
    tstop = full_config["general_pipeline_config"]["tstop"]
    directory_output = full_config["general_pipeline_config"]["directory_output"]

    args = ['--config', cosipy_yaml_input, '--config_group', 'bindata_soubk', '--overwrite', '--suffix',
            'crab_dc3', '--output-dir', directory_output, '--tmin', str(tstart), '--tmax', str(tstop)]
    cosi_bindata(argv=args)


def execute_bindata_background(cosipy_yaml_input, lib_dir):
    import cosipy
    from cosipy.pipeline.task.task import cosi_bindata
    import subprocess
    from yayc import Configurator
    print('Binning background')

    full_config = Configurator.open(cosipy_yaml_input)
    tstart = full_config["general_pipeline_config"]["tstart"]
    tstop = full_config["general_pipeline_config"]["tstop"]
    directory_output = full_config["general_pipeline_config"]["directory_output"]

    args = ['--config', cosipy_yaml_input, '--config_group', 'bindata_bk', '--overwrite', '--suffix',
            'Background_Model', '--output-dir', directory_output, '--tmin', str(tstart), '--tmax', str(tstop)]
    cosi_bindata(argv=args)


def execute_threemlfit(cosipy_yaml_input, lib_dir, fitmodel, scanvar):
    """
    Execute 3ML fitting analysis on COSI data across multiple time intervals.
    
    Parameters:
    - cosipy_yaml_input: Path to COSIPY configuration YAML file
    - lib_dir: Directory containing custom library functions
    - fitmodel: Spectral model name for fitting
    - scanvar: Flag (1 = time scan mode, 0 = external trigger mode)
    """

    # Import required packages
    import cosipy
    from cosipy.pipeline.task.task import cosi_threemlfit
    import sys
    sys.path.append(lib_dir)
    from common_functions import read_cosi_ts_detect, read_base_pipeline_params, format_override_val, read_trigger_content_multiple_yaml
    from PIL import Image, ImageDraw, ImageFont
    from threeML import JointLikelihood, DataList, XYLike, Model, PointSource, Constant
    import numpy as np

    # Load configuration from YAML file 
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)

    # Extract key parameters from configuration
    tstart = full_config["general_pipeline_config"]["tstart"]
    tstop = full_config["general_pipeline_config"]["tstop"]
    directory_output = full_config["general_pipeline_config"]["directory_output"]


    # Initialize measurement variables for source location and significance
    measured_l = float(0.)
    measured_b = float(0.)
    error_coo = float(0.)
    maxumumTS = float(0.)

    # Format spectral model parameters for command-line override
    # Returns: 8 override parameters and the model name
    var_override1, var_override2, var_override3, var_override4, var_override5, var_override6, var_override7, var_override8, modelname = format_override_val(fitmodel, measured_l, measured_b, error_coo)

    # Build command-line arguments for 3ML fitting task
    args = ['--config', cosipy_yaml_input, '--config_group', 'threemlfit_'+modelname, '--override', 
                var_override1, var_override2, var_override3, var_override4, var_override5,
                var_override6, var_override7, var_override8, '--overwrite', '--suffix', 
                modelname, '--output-dir', directory_output]

    # Perform the fit
    cosi_threemlfit(argv=args)


def build_spectral_fit(cosipy_yaml_input, lib_dir, modeltoplot):
    """
    Build a PDF visualization of spectral fitting results by combining individual 
    spectrum images with fitting parameters overlaid as text.
    
    Parameters:
    - cosipy_yaml_input: Path to COSIPY configuration YAML file
    - lib_dir: Directory containing custom pipeline functions
    - modeltoplot: Spectral model name to extract and visualize (e.g., 'fit_spectrum_pw')
    """
    
    # Import required packages
    import cosipy
    from cosipy.pipeline.task.task import cosi_bindata
    from PIL import Image, ImageDraw, ImageFont
    import os
    import re
    import math
    import sys
    import h5py

    # Add library directory to Python path for custom imports
    sys.path.append(lib_dir)
    from common_functions import read_cosi_ts_detect, read_base_pipeline_params, read_spectral_fit_info, read_trigger_content_multiple_yaml

    # Load configuration from YAML file
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)

    # Extract key parameters from configuration
    tstart = full_config["general_pipeline_config"]["tstart"]
    tstop = full_config["general_pipeline_config"]["tstop"]
    directory_output = full_config["general_pipeline_config"]["directory_output"]

#    externalTrigger_start, externalTrigger_stop, flag_trigger = read_trigger_content_multiple_yaml(
#        lib_dir, trigger_list)


    # ========== FIND FITTING RESULT FILES ==========
    # Search for HDF5 fitting result files from spectral analysis
    nameFiles_fit = []
    for f in os.listdir(directory_output):
        # Only process HDF5 files matching the specified model (not in timescan/)
        if f.lower().endswith(".h5") and str(modeltoplot) in f:
            fileName = directory_output + f
            nameFiles_fit.append(fileName)
            print(f)

    # Sort analysis files by the second-to-last number in filename
    nameFiles_fit_sorted = sorted(
        nameFiles_fit,
        key=lambda f: int(re.findall(r'\d+', f)[-1]) if len(re.findall(r'\d+', f)) >= 1 else 0
    )


    # ========== FIND AND SORT PNG IMAGE FILES ==========
    pages = []  # List to accumulate PDF pages
    pngs = []  # List to accumulate PNG files
#    timeFiles = []  # List to store time values for labels

    # Add spectral fit PNG files to the sorted list
    for t in range(len(nameFiles_fit_sorted)):
        pngs.append(directory_output+'/raw_spectrum_' +
                           modeltoplot+'.png')

    # ========== SETUP COUNTERS AND FONTS ==========
    frame_numtot = len(pngs)  # Total number of images
#    frame_numtot_external = len(externalTrigger_start)  # Number of external trigger images
    num_fitmodels = len(nameFiles_fit_sorted)  # Number of fit models
    frameNum = 0  # Current frame counter

    # ========== LOOP THROUGH EACH IMAGE AND OVERLAY FITTING PARAMETERS ==========
    for path in pngs:
        # Load PNG spectrum image
        img = Image.open(path)
        # Create transparent overlay layer for text
        txt = Image.new("RGBA", img.size)

        # Define fonts for different text sizes
        font = ImageFont.truetype("DejaVuSans.ttf", 10)
        font2 = ImageFont.truetype("DejaVuSans.ttf", 9)
        font3 = ImageFont.truetype("DejaVuSans.ttf", 20)

        # Create drawing context for text overlay
        draw = ImageDraw.Draw(txt)

        # Draw model name in red at top-right
        draw.text((600, 30), str(modeltoplot),
                  font=font3, fill=(255, 0, 0, 255))

        # Read spectral fitting parameters from result file
        name_var, value_var, errneg_var, errpos_var, unit_var = read_spectral_fit_info(
            0, directory_output, modeltoplot)
        # Draw trigger start time
        draw.text((100, 110), 'Start time =' +
                  str(tstart)+' s', font=font2, fill=(255, 0, 0, 255))
        # Draw trigger stop time
        draw.text((100, 130), 'Stop time =' +
                  str(tstop)+' s', font=font2, fill=(255, 0, 0, 255))
        # Check if fit converged
        if len(value_var) == 1:
            draw.text((90, 200), 'Fit not converging! ',
                      font=font2, fill=(255, 0, 0, 255))

        # Draw each fitting parameter with its value, errors, and units
        for uu in range(len(value_var)):
            # Parameter name (last 15 characters only)
            draw.text((90, 150+uu*20), str(name_var[uu].decode(
                "utf-8")[-15:]) + ' = ', font=font2, fill=(0, 0, 0, 255))
            # Parameter value with negative and positive errors
            draw.text((200, 150+uu*20), str(math.trunc(value_var[uu]*1000)/1000) + ' (' + str(math.trunc(
                errneg_var[uu]*10000)/10000) + ',' + str(math.trunc(errpos_var[uu]*10000)/10000) + ')', 
                font=font2, fill=(0, 0, 0, 255))
            # Unit of measurement
            draw.text((320, 150+uu*20), str(unit_var[uu].decode("utf-8")), font=font2, fill=(0, 0, 0, 255))

        # ========== COMPOSITE IMAGE AND ADD TO PDF ==========
        # Composite the text overlay onto the original spectrum image
        out = Image.alpha_composite(img, txt)

        # Convert to RGB and add to pages list
        pages.append(out.convert("RGB"))
        frameNum += 1

    # ========== SAVE AS MULTI-PAGE PDF ==========
    # Save first page and append all remaining pages into a single PDF file
    pages[0].save(
        directory_output+'raw_spectrum_'+modeltoplot+'_sequence.pdf',
        save_all=True,
        resolution=200.0,
        format="PDF",
        append_images=pages[1:])


def cleanup_and_format(cosipy_yaml_input, lib_dir):
    # some cleanup and some service directory creation

    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    import cosipy
    from contextlib import redirect_stdout
    import sys
    import subprocess
    sys.path.append(lib_dir)
    from common_functions import read_base_pipeline_params, read_trigger_content_multiple_yaml
    from threeML import JointLikelihood, DataList, XYLike, Model, PointSource, Constant

    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    tstart = full_config["general_pipeline_config"]["tstart"]
    tstop = full_config["general_pipeline_config"]["tstop"]
    directory_output = full_config["general_pipeline_config"]["directory_output"]

    # clean up old files
    subprocess.run('mkdir '+directory_output+'timescan', shell=True)
    subprocess.run('mkdir '+directory_output+'../garbagebin', shell=True)

    subprocess.run('mv '+directory_output+'tsel_* ' +
                   directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'bin* ' +
                   directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'*png ' +
                   directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'timescan/*png ' +
                   directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'timescan/*h5 ' +
                   directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'timescan/*txt ' +
                   directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'*pdf ' +
                   directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'results*h5 ' +
                   directory_output+'../garbagebin', shell=True)
