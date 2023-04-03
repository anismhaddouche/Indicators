import mysql.connector as mariadb
import json
import gzip, toml
import os
from prefect import flow, task, get_run_logger
from pathlib import Path
from utils.utils import *
from utils.components import *
from utils.diff import *
import warnings
warnings.filterwarnings("ignore")


@task(name="extract_text_init")
def extract_text_init(database: dict, logger) -> None:
    """
    Get text labdocs and possible initial texts (teacher)
    """
    # query = """
    # SELECT t1.id_labdoc, t1.id_report, t1.id_ld_origin, t1.type_labdoc, t2.name, t2.labdoc_data
    # FROM labdoc t1
    # LEFT JOIN labdoc t2 ON t2.id_labdoc = t1.id_ld_origin
    # WHERE t1.type_labdoc = 'text' AND t1.id_report IS NOT NULL
    # AND t2.labdoc_data IS NOT NULL AND t2.labdoc_data != '' AND t2.labdoc_data != '<p>.</p>'
    # ORDER BY t1.id_labdoc  ASC
    #  """

    query = """
    SELECT t1.id_labdoc, t1.id_report, t1.id_ld_origin, t1.type_labdoc, t2.name, t2.labdoc_data
    FROM labdoc t1
    LEFT JOIN labdoc t2 ON t2.id_labdoc = t1.id_ld_origin
    WHERE t1.type_labdoc = 'text' AND t1.id_report IS NOT NULL
    ORDER BY t1.id_labdoc  ASC
    """

    try:
        conn = mariadb.connect(
            user=database["user"],
            password=database["password"],
            host=database["host"],
            database=database["database_name"],
        )
    except mariadb.Error as e:
        logger.critical(f"Error connecting to MariaDB Platform: {e}")

    cur = conn.cursor()
    cur.execute(query)
    # data is on the form {'id_labdoc': labdoc_data}
    data = {}
    for row in cur:
        data[row[0]] = row[5]
    cur.close()
    conn.close()
    with gzip.open(
        "data/tmp/0_labdocs_texts_init.json.gz", "wt", encoding="utf-8"
    ) as zipfile:
        json.dump(data, zipfile, ensure_ascii=False, indent=4)

    logger.info(f"The total number of LabDoc is {len(data.keys())}")


# ----------------------------------------------------------------------------------------
@task(name="extract_text")
def extract_text(config: dict, logger) -> None:
    """
    Description:

    Extracts the text of each version of labdoc by removing the html tags and clean texts according to regex patterns.
    -------

    output:
    dict[id_report][id_labdoc] = list([text, user, id_trace])`
    exemple:
        {"29502":
           {"272580": [
              ["Les plus importantes...", "8514", 5541929],
              ["Les Plus importantes...", "8513", 5541935]]
           }
        }
    """
    regex_text_patterns = config["regex_text_patterns"]
    id_missions = selected_missions(config["missions"])

    # Get id's of initial labdocs texts
    with gzip.open(
        "data/tmp/0_labdocs_texts_init.json.gz", "rt", encoding="utf-8"
    ) as zipfile:
        labdoc_text_init = json.load(zipfile)
    # pbar = tqdm.tqdm(total=len(id_missions),ascii=' >=',colour='green',desc='Missions')
    nb_missions = 0
    nb_labdocs = 0
    logger.info(f"Number of missions in the versioning folder = {len(id_missions)}")
    for id_mission in id_missions:
        data_out = {}
        path = f"data/versioning/{id_mission}/"
        labdocs_filenames = [
            f
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f)) and not f.startswith(".")
        ]
        for labdoc_filename in labdocs_filenames:
            labdoc = str(int(labdoc_filename[:-8]))
            if labdoc in labdoc_text_init:
                nb_labdocs += 1
                with gzip.open(
                    path + labdoc_filename, "rt", encoding="utf-8"
                ) as zipfile:
                    if zipfile:
                        data_in = json.load(zipfile)
                        id_report = data_in["id_report"]
                        id_labdoc = data_in["id_labdoc"]
                        if id_report not in data_out:
                            data_out[id_report] = {}
                        if id_labdoc not in data_out[id_report]:
                            data_out[id_report][id_labdoc] = []
                            # Etat initial
                            initial_html = labdoc_text_init[labdoc]
                            if initial_html:
                                initial_text = clean_text(
                                    initial_html, regex_text_patterns
                                )
                                if initial_text:
                                    # data_out[id_report][id_labdoc].append([{'text':initial_text,'id_user':'ens','id_trace':0}])
                                    data_out[id_report][id_labdoc].append(
                                        [initial_text, "ens", 0]
                                    )
                        for content in data_in["contents"]:
                            id_user = content["id_user"]
                            id_trace = content["id_trace"]
                            html = content["data"]
                            if html:
                                text = clean_text(html, regex_text_patterns)
                                if text:
                                    # data_out[id_report][id_labdoc].append([{'text':text,'id_user':str(id_user),'id_trace':id_trace}])
                                    data_out[id_report][id_labdoc].append(
                                        [text, str(id_user), id_trace]
                                    )
                        if not data_out[id_report][id_labdoc]:
                            del data_out[id_report][id_labdoc]
        if data_out:
            Path("data/tmp/0_missions_texts").mkdir(parents=True, exist_ok=True)
            with gzip.open(
                f"data/tmp/0_missions_texts/{id_mission}.json.gz", "wt", encoding="utf-8"
            ) as zipfile:
                json.dump(data_out, zipfile, ensure_ascii=False, indent=-1)
        nb_missions += 1
        logger.info(
            f"Mission {id_mission} finished. There is still {len(id_missions) - nb_missions} missions"
        )
    logger.info(f"Number of mission treated =  {nb_missions}")
    logger.info(f"Number of labdoc treated =  {nb_labdocs}")


# ----------------------------------------------------------------
@flow(
    name="flow_0",
    description="First, get the id of text labdocs as well as the initial texts (with html tags) written by teachers. These step need access to the local database  LabNbook, Secondly, extracts the text of each version of labdoc by removing the html tags and clean texts according to regex patterns.",
)
def run_flow_0(config: dict):
    logger = get_run_logger()
    try:
        extract_text_init(config["database"], logger=logger)
        extract_text(config, logger=logger)
    except Exception as e:
        logger.critical(f"The following Exception occurred {e}")


if __name__ == "__main__":
    with open("pyproject.toml", "r") as f:
        config = toml.loads(f.read())
    run_flow_0(config=config)
