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


def make_dashboard():
    """
    description #TODO
    """
    #-- Prepare data
    summary_all  = pd.read_csv('/Users/anis/test_labnbook/Indicators/data/tmp/reports/summary_all.csv', index_col = [0])
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_mission = st.selectbox('Select a mission', np.sort(summary_all["id_mission"].unique()))
    with col2:
        selected_report = st.selectbox("Select a report", np.sort(summary_all[summary_all["id_mission"]==selected_mission]["id_report"].unique()))
    with col3:
        selected_labdoc = st.selectbox("Select a labdoc", np.sort(summary_all[summary_all["id_report"]==selected_report]["id_labdoc"].unique()))  
    summary_labdoc = summary_all[summary_all["id_labdoc"] == int(selected_labdoc)]
    summary_labdoc.drop(['id_mission','id_report','id_labdoc'],axis =1, inplace = True)
    summary_labdoc['action_time'] = pd.to_datetime(summary_labdoc['action_time'])
    summary_labdoc['edition_time'] = summary_labdoc['action_time'].diff()
    summary_labdoc["id_trace"] = summary_labdoc["id_trace"].astype(str)
    summary_labdoc.set_index('id_trace',inplace=True)
    summary_labdoc['1-sim'] = 1 - summary_labdoc["sim"]
    edition_time = summary_labdoc['edition_time']
    summary_labdoc["edition_time"] = summary_labdoc["edition_time"].astype(str)

    # --- Metrics 
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Nomber de tokens", summary_labdoc["n_tokens"].iloc[-1])
    col2.metric("Nombre de co-auteur", summary_labdoc["n_users"].iloc[-1])
    try : 
        col3.metric("Plage de travail",str(summary_labdoc['action_time'].iloc[-1] - summary_labdoc['action_time'].iloc[1] ))
    except :
        col3.metric("Plage de travail",0)
    col4.metric("Nombre de segments",summary_labdoc['n_segments'].iloc[-1] )
    col5.metric("Co-écriture",summary_labdoc['coec'].iloc[-1].round(2) )
    col6.metric("Èquilibre de contribution",summary_labdoc['eqc'].iloc[-1].round(2))


    # --- Charts 
    df_chart_1 = summary_labdoc[['eqc','coec','1-sim']]
    st.line_chart(df_chart_1)
    st.line_chart(edition_time.apply(lambda x: x.total_seconds() / 3600))

    # --- Tables

    # --- Json
    if st.button('Détails'):
        summary_labdoc = summary_labdoc.reindex(columns=['action_time','edition_time','n_tokens','n_segments','teacher','user','sim','eqc', 'coec','1-sim'])
        st.dataframe(summary_labdoc)
        with gzip.open(f'data/tmp/0_missions_texts/{selected_mission}.json.gz', 'r') as f:
                data = json.load(f)

        labdoc = json.dumps(data[str(selected_report)][str(selected_labdoc)], indent=4, ensure_ascii=False)
        st.code(labdoc, language="json")


if __name__ == "__main__":
     make_dashboard()