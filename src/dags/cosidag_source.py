import sys
sys.path.append("/home/gamma/airflow/modules")
from datetime import datetime
from cosidag import COSIDAG
from cosidag import cfg
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import ExternalPythonOperator,BranchPythonOperator
from numpy import ndarray
from airflow.utils.trigger_rule import TriggerRule

#def monitor_data():
#    directory_monitor = "/home/gamma/workspace/data/obs/"
#    return directory_monitor

def build_custom(dag):
    # ==============================================
    # 1. External interpreters + library dirs (same conventions as other DAGs)
    # ==============================================
    EXTERNAL_PYTHON_COSIPY = cfg("EXTERNAL_PYTHON_COSIPY", "/home/gamma/envs/cosipy_laura/bin/python")
    LIB_DIR_MONITORED_SOURCE_PIPELINE = cfg(
        "COMPREHENSIVE_LIB_DIR",
        "/home/gamma/airflow/pipeline/monitored-source-pipeline.cfmodule/monitored-source-pipeline/",
    )

    cosipy_yaml_input_file = "/home/gamma/workspace/data/pipeline_MonitoredCrab.yaml"
    
    detected_folder="/home/gamma/workspace/data/obs/"

    

    #######################################
    # bin source file
    
    def binning_data(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import execute_bindata_crab
        execute_bindata_crab(config_path,lib_dir)

    ged_data_binning = ExternalPythonOperator(
        task_id="Data_Binning",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=binning_data,
        op_kwargs={
            "config_path": cosipy_yaml_input_file,
            "lib_dir": LIB_DIR_MONITORED_SOURCE_PIPELINE,
        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # bin background file
    def binning_data_bk(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import execute_bindata_background
        execute_bindata_background(config_path,lib_dir)

    ged_data_binning_bk = ExternalPythonOperator(
        task_id="Background_Binning",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=binning_data_bk,
        op_kwargs={
            "config_path": cosipy_yaml_input_file,
            "lib_dir": LIB_DIR_MONITORED_SOURCE_PIPELINE,
        },
        dag=dag,
    )
    #######################################
   
    #######################################
    # Spectral fit 
    def execute_spectral_fit(config_path: str, lib_dir: str,model_fit: int, scan_flag: int):
        """
        Wrapper function to execute 3ML spectral fitting on COSI data.
    
        Parameters:
        - config_path: Path to COSIPY configuration YAML file
        - lib_dir: Directory containing custom pipeline functions
        - model_fit: Index for spectral model (0=power law, 1=band)
        - scan_flag: Time analysis mode (0=external trigger, 1=time scan)
        """
        import sys
        sys.path.append(lib_dir)
        from pipeline_functions import execute_threemlfit

        # Call the main 3ML fitting function with provided parameters
        execute_threemlfit(config_path,lib_dir,model_fit,scan_flag)
    
    # ========== EXTERNAL TRIGGER MODE FITTING TASKS ==========
    # Create 3ML spectral fitting tasks for externally triggered events
    fittask_externaltrigger = []

    modelname="fit_spectrum_pw"

    # Create Airflow task that runs Python code in isolated cosipy environment
    t = ExternalPythonOperator(
        task_id=modelname,
        python=EXTERNAL_PYTHON_COSIPY,  # Specifies the cosipy environment interpreter
        python_callable=execute_spectral_fit,
        op_kwargs={
            "config_path": cosipy_yaml_input_file,
            "lib_dir": LIB_DIR_MONITORED_SOURCE_PIPELINE,
            "model_fit": 0,
            "scan_flag": 0,
        },

    )
    # Add task to list for later DAG dependency definition
    fittask_externaltrigger.append(t)

       
    #######################################

    #######################################
    # Build spectral fit pdf
    def build_spectral_pdf(config_path: str, lib_dir: str,model_merge: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import build_spectral_fit
        build_spectral_fit(config_path,lib_dir,model_merge)

    merge_spectral_fit_multiple = []
    modelname="pw"

    t = ExternalPythonOperator(
        task_id='merge_spectral_fit_plots_'+modelname,
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=build_spectral_pdf,
        op_kwargs={
            "config_path": cosipy_yaml_input_file,
            "lib_dir": LIB_DIR_MONITORED_SOURCE_PIPELINE,
            "model_merge": modelname
        },
    )
    merge_spectral_fit_multiple.append(t)

    #######################################
    
    #######################################
    # Clean up and format
#    def cleanup_funct(config_path: str, lib_dir: str):
#        import os
#        import sys
#        import yaml
#        sys.path.append(lib_dir)

#        from pipeline_functions import cleanup_and_format
#        cleanup_and_format(config_path,lib_dir)

#    cleanup_task = ExternalPythonOperator(
#        task_id="Cleanup_function",
#        python=EXTERNAL_PYTHON_COSIPY,
#        python_callable=cleanup_funct,
#        op_kwargs={
#            "config_path": cosipy_yaml_input_file,
#            "lib_dir": LIB_DIR_MONITORED_SOURCE_PIPELINE,
#        },
#        dag=dag,
#    )
    #######################################
    
    join = EmptyOperator(task_id="join")
    join2 = EmptyOperator(task_id="join2")

    ######### wiring definition #####
    [ged_data_binning, ged_data_binning_bk] >> join
    join >> fittask_externaltrigger >> join2
    join2 >> merge_spectral_fit_multiple

   ################################
    
with COSIDAG(
    dag_id="cosidag_source",
    monitoring_folders="",
    auto_retrig=False,
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    file_patterns=None,
    select_policy="first",
    only_basename="ged",
    prefer_deepest=True,
    idle_seconds=5,
    level=1,
    build_custom=build_custom,
    tags=["example"],
):
    pass
