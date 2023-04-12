from pathlib import Path
import json
import pandas as pd
import numpy as np
import gzip
from prefect import task, flow, get_run_logger
import mysql.connector as mariadb
import toml
from utils.utils import get_writing_time
import warnings
warnings.filterwarnings("ignore")
# --------

@task(name = "summary_nonsemantic_indicators")
def summary_nonsemantic_indicators_csv(Path: str) -> pd.DataFrame:
    """
    Create a csv summary file for the nonsemantic indicators (co-writing and the balance of contribution)

    Args
    --------
    Path : the path to the file "2_collab.json.gz" 

    Returns
    --------
    A dataframe and the csv file data/tmp/reports/summary_nonsemantic_indicators.csv
    """
    with gzip.open(Path) as f:
        data = json.loads(f.read())
    results = []
    id_missions = data.keys()
    # for each mission
    for id_mission in id_missions:
        id_reports = data[id_mission].keys()
        # for each report
        for id_report in id_reports:
            id_labdocs = data[id_mission][id_report].keys()
            # for each labdoc
            for id_labdoc in id_labdocs:
                # for each trace
                id_traces = list(data[id_mission][id_report][id_labdoc].keys())
                for _,id_trace in enumerate(id_traces): 
                    row = data[id_mission][id_report][id_labdoc][id_trace]
                    if row[2] > -1 or row[3] > -1:
                        result = [
                            id_mission,
                            id_report,
                            id_labdoc,
                            id_trace,
                            row[0],
                            row[1],
                            row[5]["NB_TOKS"],
                            row[5]["NB_SEGS"],
                            row[2],
                            row[3],
                        ]
                        results.append(result)

    df = pd.DataFrame(
        results,
        columns=[
            "id_mission",
            "id_report",
            "id_labdoc",
            "id_trace",
            "n_users", # teacher is included
            "teacher",
            "n_tokens",
            "n_segments",
            "eqc",
            "coec",
        ],
    )
    df.to_csv("data/tmp/reports/3_summary_nonsemantic_indicators.csv")
    return df

# --------

@task(name = "semantic_indicator")
def semantic_indicator_csv(Path: str) -> pd.DataFrame:
    """
    Compute a csv file which resume  semantic indicator  result unsing the parameters in the config file.

    Args
    ------
    Path : The path to the a json file (semantic.json) 
    Returns
    ------
    A dataframe and the csv file "data/tmp/reports/summary_semantic_indicator.csv"
    """
    with open(Path) as f:
        data = json.loads(f.read())
    results = []
    id_missions = data.keys()
    # for each mission
    for id_mission in id_missions:
        id_reports = data[id_mission].keys()
        # for each report
        for id_report in id_reports:
            id_labdocs = data[id_mission][id_report].keys()
            # for each labdoc       
            for id_labdoc in id_labdocs:
                # for each trace
                id_traces = list(data[id_mission][id_report][id_labdoc].keys())
                for _,id_trace in enumerate(id_traces):
                    row = data[id_mission][id_report][id_labdoc][id_trace]
                    result = [
                        id_mission,
                        id_report,
                        id_labdoc,
                        id_trace,
                        row[0],
                        row[1]
                        # row[5]["NB_SEGS"],
                        # row[2],
                        # row[3],
                    ]
                    results.append(result)

    df = pd.DataFrame(
        results,
        columns=[
            "id_mission",
            "id_report",
            "id_labdoc",
            "id_trace",
            "user",
            "sim",
        ],
    )
    df.to_csv("data/tmp/reports/3_summary_semantic_indicator.csv")
    return df

# ----------

@task(name = "get_times")
def get_times(config_db:dict, df_summary_nonsemantic_indicators:pd.DataFrame, df_semantic_indicator:pd.DataFrame):
    """
    Compute some metrics depending on the time

    Args
    -----
    config_db: a dict containing the config of the database
    df_summary_nonsemantic_indicators: A Dataframe
    df_semantic_indicator : Dataframe

    Returns
    times.json : contain for each labdoc a number of modification of each author a edition time 
    summary_all.csv : A summary of some metrics of all labdocs
    -----
    """
    df_all_0 = pd.merge(df_summary_nonsemantic_indicators,df_semantic_indicator,"inner")

    try:
        conn = mariadb.connect(user=config_db['user'], password=config_db['password'],
                        host=config_db['host'], database=config_db['database_name'])
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    pass
    cursor = conn.cursor()
    # -----
    id_trace = df_all_0["id_trace"]
    trace = pd.read_sql(f" SELECT id_labdoc, id_trace ,action_time from trace WHERE  id_trace in {tuple(id_trace)} Order By  id_trace ASC", conn)
    df_all_0["id_trace"] = df_all_0["id_trace"].astype(np.int64)
    df_all_0["id_labdoc"] = df_all_0["id_labdoc"].astype(np.int64)
    # print(trace.info(),'\n',df_all_0.info())
    df_all = pd.merge(trace, df_all_0, 'right')
    df_all.to_csv("data/tmp/reports/summary_all.csv")
    # -----
    id_labdoc = df_all_0["id_labdoc"]
    # trace = pd.read_sql( f" SELECT id_trace,id_labdoc,id_user, action_time from trace WHERE id_labdoc in {tuple(id_labdoc)}  AND id_action=9 Order By id_labdoc ASC, action_time ASC", conn)
    # trace = pd.read_sql(
    # f" SELECT id_trace, id_labdoc,id_user ,id_action, action_time from trace WHERE id_labdoc in {tuple(id_labdoc)}  Order By id_labdoc ASC, action_time ASC", conn)
    trace = pd.read_sql(
    " SELECT id_trace, id_labdoc,id_user ,id_action, action_time from trace Order By id_labdoc ASC, action_time ASC", conn)
    res = {}
    for selectec_labdoc in id_labdoc:
       res[selectec_labdoc] = get_writing_time(selectec_labdoc,trace)
            
    with open("data/tmp/reports/3_times.json", "w") as f :
        json.dump(res,f)

# ----------

@flow(name ="flow_3", description = "Create some reports (indicators, number of word....)")
def run_flow_3(config:dict):
    config_db = config['database']
    logger = get_run_logger()
    try:
        df_semantic_indicator = semantic_indicator_csv("data/tmp/2_semantic.json")
        df_summary_nonsemantic_indicators = summary_nonsemantic_indicators_csv("data/tmp/2_collab.json.gz")
        get_times(config_db, df_summary_nonsemantic_indicators, df_semantic_indicator)
        logger.info("Flow was run succefully")
    except Exception as e:
        logger.critical(f"The flow did not execute correctly. The following exception occurred{e}")

if __name__ == "__main__":
    with open("pyproject.toml", "r") as f:
        config = toml.loads(f.read())
    run_flow_3(config)





