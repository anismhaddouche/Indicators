from prefect import flow, get_run_logger, task
import json
import gzip
from pathlib import Path
import tqdm as tqdm
import spacy
from spacy.tokens import Doc
from utils.components import *
from utils.diff import *
from utils.utils import selected_missions
from typing import Dict, List, Tuple


# -----------------------------------------------------------------


# @task(name="get meta data")
def get_meta(doc: Doc) -> dict:
    """
    Get the position of entities and punctuation token's mark according to the Spacy model in "fr_LabnbookNER-0.0.0"
    output : {'ENTS':{'label1':[[star,end],[star,end]...],'label2 : [[star,end],[star,end],...]},'PUNCT':[pos1,pos2,...]}
    """
    segments = []
    tokens = []
    nb_tokens = 0
    start = 0
    # Get the start and end token position of each segment
    for seg in doc.sents:
        for token in seg:
            # tokens = [token.text for token in seg ]
            if not token.is_punct:
                tokens.append(token.text)
                nb_tokens += 1
        if nb_tokens == 0:
            segments = []
        else:
            end = nb_tokens - 1
            segments.append([start, end])
            start = end + 1
    output = {}
    # output: Dict[List[int], int, List[str],int] = {[],}
    output["SEGS"] = segments
    output["NB_SEGS"] = len(segments)
    output["TOKS"] = tokens
    output["NB_TOKS"] = nb_tokens
    return output

# -----------------------------------------------------------------

@task(
    name="contrib_and_segmentation", log_prints=True)
def contrib_and_segmentation(config: dict, path_for_flow_1: Path) -> Path:
    """
    output :
    dict[id_report][id_labdoc] = list([text, user, id_trace])
    example :
    {"29502":
        {"272580": [
      ["Les plus importantes...", "8514", 5541929],
      ["Les Plus importantes...", "8513", 5541935]]
         }
    }

    """
    # Load the spacy model
    # if not os.path.exists("data/tmp/1_missions_contribs"):
    #     os.makedirs("data/tmp/1_missions_contribs")
    nlp = spacy.load(config["nlp"]["spacy_model"])
    logger = get_run_logger()
    # Get a list of all mission
    id_missions = selected_missions(config["missions"])
    nb_missions = 0
    for selected_mission in id_missions:
        # data_out = {}
        data_out: Dict[str, Dict[str, List[Tuple[str, int, int]]]] = {"": {"": []}}
        # Get the path of each mission
        path = f"{path_for_flow_1}/{selected_mission}.json.gz"
        # Open the mission
        with gzip.open(path, "rt", encoding="utf-8") as zipfile:
            # Load the mission
            if zipfile:
                data_in = json.load(zipfile)
                for id_report in data_in:
                    data_out[id_report] = {}
                    # Loop on each labdoc of the report
                    for id_labdoc in data_in[id_report]:
                        data_out[id_report][id_labdoc] = []
                        list_of_text_user_id_trace = data_in[id_report][id_labdoc]
                        # Tokenize the text
                        list_of_text_user_id_trace = [
                            (text, user, id_trace)
                            for (text, user, id_trace) in list_of_text_user_id_trace
                        ]
                        contribution = [[], [[]], []]
                        # Loop on each version of the labdoc
                        for text_user_id_trace in list_of_text_user_id_trace:
                            doc = nlp(text_user_id_trace[0])
                            meta = get_meta(doc)
                            tokens = meta["TOKS"]
                            # tokens = [token.text for token in doc]
                            text_user = (tokens, str(text_user_id_trace[1]))
                            id_trace = text_user_id_trace[-1]
                            contribution = one_step_contribution(
                                contribution, text_user, debug=False
                            )
                            users = get_users(contribution)
                            # text = get_words(contribution)
                            collab_matrix = get_matrix(contribution)

                            # segments = meta["SEGS"]
                            data_out[id_report][id_labdoc].append(
                                [users, collab_matrix, id_trace, meta]
                            )
        Path("data/tmp/1_missions_contribs").mkdir(parents=True, exist_ok=True)
        with gzip.open(
            f"data/tmp/1_missions_contribs/{selected_mission}.json.gz",
            "wt",
            encoding="utf-8",
        ) as zipfile:
            json.dump(data_out, zipfile, ensure_ascii=False, indent=2)

        nb_missions += 1
        logger.info(
            f"Mission {selected_mission} finished. There is still {len(id_missions) - nb_missions} missions"
        )
    return Path("data/tmp/1_missions_contribs")
# ----------------------------------------------------------------

@flow(name ="flow_1")
def run_flow_1(config: dict, path_for_flow_1):
    logger = get_run_logger()
    try:
      path_for_flow_2 =  contrib_and_segmentation(config, path_for_flow_1)
    except Exception as e:
        logger.critical(f"The following Exception occurred {e}")
    return path_for_flow_2
# ----------------------------------------------------------------
# if __name__ == "__main__":
#     with open("pyproject.toml", "r") as f:
#         config = toml.loads(f.read())
#     run_flow_1(config=config, path_for_flow_1)
