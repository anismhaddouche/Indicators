import streamlit as st 
import json
import gzip 
import os 
import pandas as pd 
import numpy as np
import ujson
import warnings    
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="My Streamlit App",
    page_icon=":smiley:",
    layout="wide",
    initial_sidebar_state="expanded",
    )


# Charger les données de collab
path = "/Users/anis/test_labnbook/math_ner/indicators/tmp/collab.json"
with open(path, 'r') as f:
    data_collab = ujson.load(f)

# Charger toutes les missions
folder_path = "data/tmp/0_missions_texts"
missions = [f[:-8] for f in os.listdir(folder_path) if f.endswith('.json.gz') and f[:-8].isdigit()]
missions.sort()


col1, col2, col3 = st.columns(3)
# Ajoute un bouton selectbox à chaque colonne
with col1:
    selected_mission = st.selectbox('Select a mission', missions)
with gzip.open(f'data/tmp/0_missions_texts/{selected_mission}.json.gz', 'r') as f:
        data = json.load(f)

reports = list(data.keys())
reports.sort()
with col2:
    selected_report = st.selectbox("Select a report", reports)
labdocs = list(data[selected_report].keys())
labdocs.sort()
with col3:
    selected_labdoc = st.selectbox("Select a labdoc", labdocs)    

with open(f'data/tmp/reports/semantic.json', 'r') as f:
    semantic = json.load(f)

versions = data_collab[selected_mission][selected_report][selected_labdoc]
semantic = semantic[selected_mission][selected_report][selected_labdoc]
    # return  semantic, labdoc, versions



# ------------------------------------------------------------------------------------------------------------------
summary_all  = pd.read_csv('/Users/anis/test_labnbook/semantic_indicator/data/tmp/reports/summary_all.csv', index_col = [0])
summary_labdoc = summary_all[summary_all["id_labdoc"] == int(selected_labdoc)]
summary_labdoc.drop(['id_mission','id_report'],axis =1, inplace = True)
summary_labdoc['action_time'] = pd.to_datetime(summary_labdoc['action_time'])
summary_labdoc['edition_time'] = summary_labdoc['action_time'].diff()
summary_labdoc["edition_time"] = summary_labdoc["edition_time"].astype(str)
st.dataframe(summary_labdoc)
#------------------
# summary_labdoc['edition_time'] = summary_labdoc['edition_time'].apply(lambda x: x.total_seconds() / 60)
df_chart_1 = summary_labdoc[['eqc','coec']]
df_chart_1['1-sim'] = 1 - summary_labdoc["sim"]
st.line_chart(df_chart_1)

# ---------------------------------------------------------------------------------------------------------------------
# labdoc = json.dumps(data[selected_report][selected_labdoc], indent=4, ensure_ascii=False)
# st.code(labdoc, language="json")

# EQC = [round(version[2], 2) for version in versions.values()]
# COEC = [round(version[3], 2) for  version in versions.values()]

# chart_data = pd.DataFrame(semantic).T
# chart_data.columns = ["Author","SIM"]
# chart_data["1-SIM"] = np.round(1 - (chart_data["SIM"].values).astype(np.float64),2)
# chart_data = chart_data.assign(EQC = EQC , COEC = COEC)
# st.dataframe(chart_data)
# # cols_to_plot = st.multiselect('Select the column to draw', list(chart_data.columns))
# # st.line_chart(chart_data[cols_to_plot]) 

# columns_chart = list(chart_data.drop(columns = 'SIM').columns)
# columns_chart.pop(0)

# # -- pour tracer les extra comme durée de travail 
# data = pd.read_csv("/Users/anis/test_labnbook/semantic_indicator/data/imported/times.csv",sep = ";",index_col=[0])
# id_labdocs = list(data['id_labdoc'])
# selected_labdoc = int(selected_labdoc) 

# if selected_labdoc in id_labdocs : 
#     n_users = data[data["id_labdoc"] == selected_labdoc]["n_users"].values[0]
#     durée_écriture = data[data["id_labdoc"] == selected_labdoc]["durée_écriture"].values[0]
#     plage_travail = data[data["id_labdoc"] == selected_labdoc]["durée_écriture"].values[0]
#     passage_main =  data[data["id_labdoc"] == selected_labdoc]["passage_main"].values[0]
#     col1, col2, col3, col4, col5, col6 = st.columns(6)
#     col1.metric("Durée d'écriture", durée_écriture)
#     col2.metric("Nombre de co-auteur", n_users)
#     col3.metric("Plage de travail",plage_travail)
#     col4.metric("Nombre de passage de main",passage_main)
#     col5.metric("Co-écriture",COEC.pop() )
#     col6.metric("Èquilibre de contribution",EQC.pop() )


# else : 
#      pass


def viz_mission(): 
   
    x = 2

    # st.line_chart(chart_data[columns_chart])


if __name__ == "__main__":
    viz_mission()


