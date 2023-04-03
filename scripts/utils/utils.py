import webbrowser
from bs4 import BeautifulSoup
import re
import os 
from spacy.tokens import Doc
import numpy as np
from typing import Tuple, List
import typer
import pandas as pd 

# -----------------------------------------------------------------

def clean_text(text: str, regex_text_patterns: dict) -> str:
    """
    Clean a text using the RegEx regex_text_patterns in the toml config file "pyproject.toml". 
    Note that the order of the RegEx expressions is important and that it expression is described in the config file.
    """
    html_text = re.sub(regex_text_patterns["DATA_KATEX"]["expression"], r"> $\1$ ", text)
    # Tag the end of html paragraphs
    html_text = re.sub(regex_text_patterns["PARAGRAPH_END"]["expression"], r" § \1", html_text)
    # Extract table and add '&' character at the beginning and at the end of each table
    html_text = re.sub(regex_text_patterns["DATA_TABLE"]["expression"], r" ¥¥\1\2\3¥¥ ", html_text)
    # Tag the end of cells
    html_text = re.sub(regex_text_patterns["DATA_TABLE_CELL"]["expression"], r"¥\1", html_text)
    # Remove HTML tags
    cleaned_text = BeautifulSoup(html_text, "lxml").get_text()
    #  #### Replace " with '
    cleaned_text = cleaned_text.replace('"', "'")
    # Replace a consecutive repetition of '\n' character with white space
    cleaned_text = re.sub(
        regex_text_patterns["NEW_LINES"]["expression"],
        r" ",
        BeautifulSoup(cleaned_text, "lxml").get_text(),
    )
    # Remove multiples Paragraphs end
    cleaned_text = re.sub(
        regex_text_patterns["MULTIPLE_END_PARAGRAPHS"]["expression"], r"§", cleaned_text
    )
    # Remove doulbe §§ in the end of labdocs
    cleaned_text = re.sub(
        regex_text_patterns["MULTIPLE_END_PARAGRAPHS_IN_END_LABDOC"]["expression"],
        r"",
        cleaned_text,
    )
    # Replace .§ with .
    cleaned_text = re.sub(
        regex_text_patterns["PARAGRAPH_END-DOT"]["expression"], r".", cleaned_text
    )
    # Replace consecutive repetition of '.' character with a single '.'
    cleaned_text = re.sub(regex_text_patterns["DOTS"]["expression"], r".", cleaned_text)
    # Delete '_' character to avoid problems like '______' with the tokenizer
    cleaned_text = re.sub(regex_text_patterns["UNDERSCORES"]["expression"], r"", cleaned_text)
    # Replace a consecutive repetition of '\n' character with white space
    cleaned_text = re.sub(regex_text_patterns["SPACES"]["expression"], r" ", cleaned_text)
    # Replace consecutive repetition of '-' character with a single '-'
    cleaned_text = re.sub(regex_text_patterns["DASHES"]["expression"], r"-", cleaned_text)
    # Replace '\'  with '\\'
    cleaned_text = re.sub(regex_text_patterns["BACKSLASH"]["expression"], r"\\\\", cleaned_text)
    # Replace for exemple ',mot'  with  ', mot '
    cleaned_text = re.sub(
        regex_text_patterns["COMA_NUMBERS"]["expression"], r"\1.\3", cleaned_text
    )
    # Replace for example 'a=  b' by 'a=b'
    cleaned_text = re.sub(
        regex_text_patterns["MATH_OP_EXTRA_SPACES"]["expression"], r"\1\2\3", cleaned_text
    )
    # For SI units like '1.5 m' which will be changed to '1.5m'
    cleaned_text = re.sub(
        regex_text_patterns["SI_UNITS_SPACE"]["expression"], r"\1\2", cleaned_text
    )
    # Replace again a consecutive repetition of '\n' character with white space
    cleaned_text = re.sub(regex_text_patterns["SPACES"]["expression"], r" ", cleaned_text)
    # Replace for example '( some_expression )' with '(some_expression )'
    cleaned_text = re.sub(
        regex_text_patterns["BRACKETS_SPACES"]["expression"], r"\1\2\3", cleaned_text
    )
    # Replace for exemple 'mot ,' with 'mot,'
    cleaned_text = re.sub(
        regex_text_patterns["WORD_SPACES_COMA-DOT"]["expression"], r"\1\2", cleaned_text
    )
    # Replace for exemple ',mot'  with  ', mot '
    cleaned_text = re.sub(regex_text_patterns["COMA_WORD"]["expression"], r"\1 \2", cleaned_text)
    # Replace for exemple "word1:  word 2" by "word1 : word 2"
    cleaned_text = re.sub(regex_text_patterns["WORD_COLON"]["expression"], r"\1 \2 ", cleaned_text)
    # Replace . § with .
    cleaned_text = re.sub(r"\.\s§", r".", cleaned_text)
    return cleaned_text

# -----------------------------------------------------------------
def selected_missions(config_missions: dict) -> List[int]:
    """
    Return a list of  missions according to the config section [missions] in the config toml file
    """
    missions: List[int] = []
    if config_missions["all"] == True : 
        missions = os.listdir("/Users/anis/test_labnbook/semantic_indicator/data/versioning")
    else :
        missions =  config_missions["subset"]
    
    missions = [int(mission) for mission in missions]
    missions.sort()
    return missions
    
# -----------------------------------------------------------------

def compute_coec_index(collab_matrix_segments: list, segments:list, users:list) -> float:
    """ 
    Compute the 'co-écriture' indicator 
    """
    # Check if the contribution matrix per segments is not  empty
    if not any(collab_matrix_segments) :
        return -1
    if len(collab_matrix_segments) == 1 : 
        return 0
    nb_users = len(users)
    if nb_users == 1 :
        return 0
    else : 
        if 'ens' in users : 
            collab_teacher_segments = collab_matrix_segments[-1] # last line is the teacher's contribution
            collab_matrix_segments = collab_matrix_segments[:-1]
            ratio = 1 - np.mean(collab_teacher_segments)
            nb_users -= 1
            if nb_users == 1:
                return  0         
        else :
            ratio = 1
            if nb_users == 1:
                return  0 
        eqc_segments = []
        weights = []
        for i,_ in enumerate(segments):
                #TODO : continuer
            weights.append(segments[i][1] - segments[i][0]+1)
            eqc_segments.append((np.round(1 - np.sqrt(((nb_users / (nb_users- 1)) * sum((np.array(collab_matrix_segments)[:,i]- (1/nb_users))**2))),2)))
        coec_index = ratio*(np.round(np.average(np.array(eqc_segments), weights=np.array(weights)),2))

        return coec_index


# ----------------------------------------------------------------------------------------------------------------------

def compute_eqc_index(collab_matrix :list,users: list) -> float: 
    """ 
    Compute the 'equilibre de contribution' indicator 
    """

    # Check if the contribution matrix is empty 
    if not any(collab_matrix) :
        return -1
    nb_users = len(users)
    if nb_users == 1 :
        return 0
    else : 
        if 'ens' in users : 
            collab_teacher = collab_matrix[-1] # last line is the teacher's contribution
            collab_matrix = collab_matrix[:-1] # remove the teacher's contribution
            ratio = 1 - np.mean(collab_teacher)
            nb_users -= 1
            if nb_users == 1:
                return  0       
        else :
            ratio = 1
            if nb_users == 1:
                return  0
        collab_users = np.round(np.mean(collab_matrix,axis = 1),2)
        eqc_index = ratio*(np.round(1 - np.sqrt(((nb_users / (nb_users- 1)) * sum((collab_users - (1/nb_users))**2))),2))
    return eqc_index

# ----------------------------------------------------------------------------------------------------------------------

def compute_contrib_matrix_segments(collab_matrix: list,segments: list) -> list:
    """
    Compute the contribution matrix of each segment for each user (including the teacher)
    """
    collab_matrix_segments=[]
    for i, user_contrib in enumerate(collab_matrix): # on boucle sur les lignes
        user_contrib_seg = []
        nb_tokens_seg = [seg[1] - seg[0] + 1 for seg in segments]
        for j, seg in enumerate(segments):
            #__________________________
            if nb_tokens_seg[j] == 0:
                user_contrib_seg.append(1)
            else:
                score = np.round(sum(user_contrib[seg[0]:seg[1]+1]) / nb_tokens_seg[j],2)
                user_contrib_seg.append(score)
            #__________________________
            # score = np.round(sum(user_contrib[seg[0]:seg[1]+1]) / nb_tokens_seg[j],2)
            # user_contrib_seg.append(score)
        collab_matrix_segments.append(user_contrib_seg)
    return collab_matrix_segments




# ----------------------------------------------------------------------------------------------------------------------

def compute_indicators(collab_matrix:list,users:list,meta:dict,id_mission : int,id_report:int,id_labdoc:int,id_trace:int,debug=False) -> Tuple[int,int,float,float,list]:
    """
    Compute the three indicators in 'compute_eqc_index' and  'compute_coec_index' and 'compute_sem_index'
    """
    #TODO: rajouter ici notre indicateur sémantique
    segments = meta['SEGS']
    #nb_segments = meta['NB_SEGS']
    #nb_tokens = meta['NB_TOKS']
    collab_matrix_segments = compute_contrib_matrix_segments(collab_matrix,segments)
    if debug == True :   
        if np.mean(np.sum(collab_matrix_segments,axis = 0)) != 1:
            typer.secho(f"The lines sum of contribution matrix of : (id_mission,id_report,id_labdoc,id_trace) = ({id_mission} {id_report} {id_labdoc} {id_trace}) differ from 1",fg = typer.colors.RED)
            print(f"contribution matrix: {collab_matrix_segments} users : {users}" )
            if len(users) in (1,2) :
                 typer.secho(f"Only the teacher or only 1 user except the teacher is in the text sequence, considered as not collaboration.",fg = typer.colors.RED)
    
    
    if 'ens' in users :
        teacher = 1
    else :
        teacher = 0


    nb_users = len(users)
    eqc_index = compute_eqc_index(collab_matrix,users)
    coec_index = compute_coec_index(collab_matrix_segments,segments,users)
    return (nb_users,teacher, eqc_index, coec_index, collab_matrix_segments)


# ----------------------------------------------------------------------------------------------------------------------

def get_authors_changes(authors : List[int]) -> List[int] :
    """
    Return a list which represent the index in the authors list where author change
    EX:
    input: authors = [10643, 10643, 10655, 10655, 10655, 1044, 1044, 1044, 1044, 10643,10643,33,33]
    output : [1, 4, 8, 10, 12]
    """
    last_indices = []
    i = 0
    while i < len(authors):
        current = authors[i]
        last_index = i
        while i < len(authors) and authors[i] == current:
            last_index = i
            i += 1
        last_indices.append(last_index)
    return  last_indices


# ----------------------------------------------------------------------------------------------------------------------

def get_writing_time(id_labdoc : int, trace : pd.DataFrame)-> dict:
    """
    Calculates the number of modification (trace 9) for each change of authors and also multiplies it by 20 or 30 to have the effective writing time 
    output : ex : {445494: [(12673, 15, 450), (12661, 2, 60), (12673, 47)]} 
    """ 
    labdoc  = trace[trace['id_labdoc'] == int(id_labdoc)]

    if labdoc.empty:
        pass
    else:
        labdoc_time = labdoc["action_time"].iloc[0]
        date_to_compare = pd.Timestamp('2020-05-16')

        if labdoc_time.date() < date_to_compare.date():
            factor = 20
        else:
            factor = 30
        count_list = []
        current_author = None
        current_count = 0
        for author in labdoc['id_user']:
            if author == current_author:
                current_count += 1
            else:
                if current_author is not None:
                    count_list.append((current_author, current_count,current_count*factor))
                current_author = author
                current_count = 1
        count_list.append((current_author, current_count,current_count*factor))
        
        return {int(id_labdoc) : count_list}

    # ----------------------------------------------------------------------------------------------------------------------

    def visualize_html(html_code: str):
        """"
        Visualize an html code.
        """
        with open("tmp/preview.html", "w") as f:
            f.write(html_code)
        try: 
            webbrowser.open("tmp/preview.html")
        except Exception as e: 
            print(f"The following error {e} occurs when previewing the file")