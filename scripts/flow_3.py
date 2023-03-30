from pathlib import Path
import json
import pandas as pd
import numpy as np
import gzip
from prefect import task, flow, get_run_logger
import mysql.connector as mariadb
import toml




@task(name = "summary_nonsemantic_indicators")
def summary_nonsemantic_indicators_csv(Path: str) -> pd.DataFrame:
    """
    description
    """
    # Unzip de file using gzip
    # result = {'id_mission':str, 'id_report':str, 'id_labdoc':str, 'id_trace':str, 'n_users':int, 'eqc_index':int, 'coec_index':int,'nb_tokens':int,'nb_segments':int}
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
                    # check if n_user >1
                    # if row[0] > 1:
                        # check if the labdc is not empty (when indicators == -1)
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
    df.to_csv("data/tmp/reports/summary_nonsemantic_indicators.csv")
    return df

#------------------------------------------------------------------------------------------------------------

@task(name = "semantic_indicator")
def semantic_indicator_csv(Path: str) -> pd.DataFrame:
    """
    Description
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
    df.to_csv("data/tmp/reports/summary_semantic_indicators.csv")
    return df



# ---------
@task(name = "")
def get_times(config_db, df_summary_nonsemantic_indicators, df_semantic_indicator):
    """
    description
    """
    df_all_0 = pd.merge(df_summary_nonsemantic_indicators,df_semantic_indicator,"inner")

    try:
        conn = mariadb.connect(user=config_db['user'], password=config_db['password'],
                        host=config_db['host'], database=config_db['database_name'])
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    pass
    cursor = conn.cursor()
    id_trace = df_all_0["id_trace"]
    trace = pd.read_sql(f" SELECT id_labdoc, id_trace ,action_time from trace WHERE  id_trace in {tuple(id_trace)} Order By  id_trace ASC", conn)
    df_all_0["id_trace"] = df_all_0["id_trace"].astype(np.int64)
    df_all_0["id_labdoc"] = df_all_0["id_labdoc"].astype(np.int64)
    # print(trace.info(),'\n',df_all_0.info())
    df_all = pd.merge(trace, df_all_0, 'right')
    df_all.to_csv("data/tmp/reports/summary_all.csv")



@flow(name ="flow_3", description = "")
def run_flow_3(config:dict):
    config_db = config['database']
    logger = get_run_logger()
    try:
        df_semantic_indicator = semantic_indicator_csv("data/tmp/reports/semantic.json")
        df_summary_nonsemantic_indicators = summary_nonsemantic_indicators_csv("data/tmp/2_collab.json.gz")
        get_times(config_db, df_summary_nonsemantic_indicators, df_semantic_indicator)
        logger.info("Flow was run succefully")
    except Exception as e:
        logger.critical(f"The flow did not execute correctly. The following exception occurred{e}")


if __name__ == "__main__":
    with open("/Users/anis/test_labnbook/semantic_indicator/pyproject.toml", "r") as f:
        config = toml.loads(f.read())
    run_flow_3(config)






# Récupération du curseu
