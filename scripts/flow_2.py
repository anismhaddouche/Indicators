
from prefect import flow, get_run_logger, task
import json
import gzip
from pathlib import Path
import tqdm as tqdm
# import spacy
from spacy.tokens import Doc
from utils.components import *
from utils.diff import *
from utils.utils import selected_missions, compute_indicators,get_authors_changes
# from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer, util
import numpy as np 


@task(name = "nonsemantic_indicators")
def nonsemantic_indicators(config_missions : dict, debug = False) :
    id_missions = selected_missions(config_missions)
    id_missions.sort()
    logger = get_run_logger()
    # id_missions = [rep[:-8] for rep in os.listdir('data/tmp/missions_contribs/') if not rep.startswith('.')]
    data_out = {}
    # data_out = {selected_mission:{id_report:{id_labdoc:{n_users,teacher ,eqc_index, coec_index, sim_index,collab_matrix_segments, meta}}}}
    #data_out = {int:{int:{int:{int,int,float,float,float,list,dict}}}} 
    #Loop on missions
    # pbar = tqdm.tqdm(total=len(id_missions), ascii=' >=',colour='green',desc='Missions')
    nb_missions = 0
    for selected_mission in  id_missions:
    # for selected_mission in id_missions:
        path = f"data/tmp/1_missions_contribs/{selected_mission}.json.gz"
        with gzip.open(path, 'rt', encoding='utf-8') as zipfile:
            if zipfile:
                data_in = json.load(zipfile)
                data_out[selected_mission] = {}
                #Loop on reports
                for id_report in data_in:
                    data_out[selected_mission][id_report] = {}
                    #Loop on labdocs
                    for id_labdoc in data_in[id_report]:
                        data_out[selected_mission][id_report][id_labdoc] = {}
                        # print(f"{selected_mission} {id_report} {id_labdoc}")
                        #data_out[id_report][id_labdoc].append([users, matrix, id_trace, meta])
                        for elt in data_in[id_report][id_labdoc]:
                            # users, matrix, segments, id_trace, _ , meta = elt
                            users, collab_matrix, id_trace, meta = elt
                            #typer.secho(f"--- Calcul de collaboration : traitement du labdoc {id_labdoc} ---", fg=typer.colors.RED)
                            n_users,teacher,eqc_index, coec_index ,collab_matrix_segments  = compute_indicators(collab_matrix, users, meta,selected_mission,id_report,id_labdoc,id_trace,debug)
                            # La contribution d'un enseignant seul n'est pas stocké
                            if (n_users, eqc_index )!= (0, 0):
                                data_out[selected_mission][id_report][id_labdoc][id_trace] = [n_users,teacher ,eqc_index, coec_index,collab_matrix_segments, meta]
                        # Les contributions vides sont omises

                        if not data_out[selected_mission][id_report][id_labdoc]:
                            del data_out[selected_mission][id_report][id_labdoc]
                    if not data_out[selected_mission][id_report]:
                        del data_out[selected_mission][id_report]
                if not data_out[selected_mission]:
                    del data_out[selected_mission]
        nb_missions+=1 
        logger.info(
            f"Mission {selected_mission} finished. There is still {len(id_missions) - nb_missions} missions"
        )
    with gzip.open(f"data/tmp/2_collab.json.gz", 'wt', encoding='utf-8') as zipfile:
        json.dump(data_out, zipfile, ensure_ascii=False)



@task(name="semantic_indicator")
def semantic_indicator(config_nlp : dict,config_missions : dict ):
    """
    Compute the semantic indicators thanks to the model speciefied in config["nlp"]
    """
    logger = get_run_logger()
    model = SentenceTransformer(config_nlp)
    id_missions = selected_missions(config_missions)
    id_missions.sort()
    score_missions = {}
    nb_missions = 0
    for selected_mission in id_missions : 
        with gzip.open(f'data/tmp/0_missions_texts/{selected_mission}.json.gz', 'r') as f:
                data = json.load(f)
        reports = list(data.keys())
        score_report = {}
        for selected_report in reports:
            labdocs = list(data[selected_report].keys())
            score_labdoc = {}
            # For each Labdoc ----
            for selected_labdoc in labdocs:
                versions_labdoc = data[selected_report][selected_labdoc]
                #print(type(versions_labdoc), versions_labdoc)
            # Ici versions_labdoc contient toute les versions du Labdoc sous la forme [["text","id_teacher",id_trace,[text,id_teacher,id_trace ]]
                # print(versions_labdoc, type(versions_labdoc))
                authors = []
                for _, author in enumerate(versions_labdoc):
                    try:
                        authors.append(int(author[1]))
                    except:
                        authors.append(author[1])
                id_authors_changes = get_authors_changes(authors)
                embeddings = {}
                authors = []
                # Garder que les version ou l'auteur change 
                versions_labdoc = [versions_labdoc[i] for i in id_authors_changes]
                for i,version in enumerate(versions_labdoc):
                    text = version[0]
                    author = version[1]
                    authors.append(author)
                    id_trace = version[2]
                    embedding = model.encode(text, convert_to_tensor=True)
                    embeddings[id_trace] = embedding
                keys = list(embeddings.keys())
                cosine_scores = {}
                cosine_scores[keys[0]] = 1
                for i in range(len(keys) - 1):
                    a = keys[i]
                    b = keys[i+1]
                    cosine_score = np.round(util.cos_sim(embeddings[a], embeddings[b])[0][0].tolist(),2)
                    # cosine_score = 1
                    cosine_scores[b] = cosine_score
                result = {}
                for k, v, i in zip(cosine_scores.keys(), cosine_scores.values(),range(len(authors))):
                    result[k] = (authors[i], v)
                score_labdoc[selected_labdoc] = result
                #print(type(cosine_scores),cosine_scores)
                #score_labdoc[selected_labdoc] = list(zip(cosine_scores,authors))
            score_report[selected_report] = score_labdoc
        score_missions[selected_mission] = score_report
        nb_missions +=1
        logger.info(f"Mission {selected_mission} finished. There is still {len(id_missions) - nb_missions} missions")

    Path("data/tmp/reports").mkdir(parents=True, exist_ok=True)
    with open("data/tmp/2_semantic.json", "w") as f:
        json.dump(score_missions, f)




@flow(name ="flow_2", description = "Compute all indicators (co-écriture, équilibre de contribution and the 'semantique' indicator)")

def run_flow_2(config: dict):
    logger = get_run_logger()
    try:
        nonsemantic_indicators(config["missions"])
        semantic_indicator(config["nlp"]["model"],config["missions"])
        logger.info("Flow was run succefully")
    except Exception as e:
        logger.critical(f"The flow did not execute correctly. The following exception occurred{e}")


if __name__ == "__main__":
    with open("pyproject.toml", "r") as f:
        config = toml.loads(f.read())
    run_flow_2(config=config)
