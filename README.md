# monitored-source-pipeline
Automated pipeline for COSI's monitored sources - still a work in progress! $${\color{red} Proceed \space with \space caution!}$$

The Monitored Source Pipeline is a COSIflow module for routine analysis of known sources observed by the COSI mission. It is a stripped-down version of the [Comprehensive Transient Pipeline](https://github.com/cositools/comprehensive-transient-analysis-pipeline/tree/main) and relies on Laura's COSIpy pipeline functions.

## Install
Following the [Fast Transient Pipeline](https://github.com/cositools/fast-transient-analysis-pipeline/tree/dev-review) install
```
cd ~/cosi
git clone https://github.com/cositools/monitored-source-pipeline.git
cd monitored-source-pipeline/env/bin
./install
```

The installer prompts for the local configuration, clones COSIflow beside this repository when necessary, builds the required environments, starts the services, and loads the Monitored Source Pipeline module. Let it finish before continuing.

## Download and store files
The current version of the pipeline fits the Crab nebula with a power-law function. To do this, you'll need to download the DC3 Crab simulation, the response, the background, and the SC orientation file, and add them to the cosiflow data directory. You may need to define the directories, if they don't already exist from another pipeline. Place the files as shown below:
```
COSItools/cosiflow/data/obs/2025_01/250101/ged/crab_powerlaw_3months_unbinned_data_filtered_with_SAAcut.fits
COSItools/cosiflow/data/obs/2025_01/250101/auxil/ResponseContinuum.o3.e100_10000.b10log.s10396905069491.m2284.filtered.nonsparse.binnedimaging.imagingresponse.h5
COSItools/cosiflow/data/obs/2025_01/250101/auxil/Total_BG_without_SAAcomponent_3months_unbinned_data_filtered_with_SAAcut.fits
COSItools/cosiflow/data/obs/2025_01/250101/auxil/DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth_SAA.ori
```
Move the ```pipeline_MonitoredCrab.yaml``` file from this git repo to ```COSItools/cosiflow/data```. This is the file that defines the fit functions and source parameters for the analysis.

## Start the pipeline
The Monitored Source Pipeline is triggered manually and looks for data in the ```/home/gamma/workspace/data/obs/``` docker directory. First, start the cosiflow docker (and reference the [cosiflow documentation](https://github.com/cositools/cosiflow/tree/dev-review) for more details):

```docker compose up```

With the default ports, open the Airflow web interface: [http://localhost:8080/home](http://localhost:8080/home).

Sign in to Airflow with the administrator credentials selected during installation. The DAG list should contain ```cosidag_source```, in addition to any other pipelines you have installed.

Manually trigger the DAG in the Airflow UI and things should run! 

The pipeline current has four main tasks:
1. Data binning
2. Background binning
3. Spectral fit
4. Merging fit results into plots

Note that the background binning takes ~7 minutes to run, and I personally had to increase the Docker memory to 64 GB to run 1 month of background binning without it crashing. Check your current memory usage with ```docker stats cosi_airflow``` and increase the allocation in the ```cosiflow/env/docker-compose.yaml``` file (line 114):

```
  airflow:
    image: cosiflow-airflow:native
+   mem_limit: 64g          # Add this line
+   memswap_limit: 64g      # Add this line
    build:
```

## Check the results
The Airflow UI will show the cosidag_source was successful. You can find the results in the ```cosiflow/data/source/crab``` directory and there should be 8 files produced:
1. bin_crab_dc3.yaml
2. bin_Background_Model.yaml
3. tsel_unbinned_data_crab_dc3.fits (178 MB)
4. tsel_binned_data_galactic_crab_dc3.hdf5 (85 MB)
5. tsel_unbinned_data_Background_Model.fits (6.3 GB)
6. tsel_binned_data_galactic_Background_Model.hdf5 (220 MB)
7. results_pw.h5
8. raw_spectrum_pw.png


Please let me know if you have any feedback!

