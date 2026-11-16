import os
import pandas as pd
import streamlit as st

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'leaf_data.csv')

SPECIES_LIST = ['은행', '단풍', '벚나무', '감나무', '밤나무', '화살나무']

def load_default_df():
    df = pd.read_csv(DEFAULT_CSV_PATH)
    df['가짜여부'] = df['가짜여부'].astype(bool)
    return df

def get_leaf_df():
    if 'leaf_df' not in st.session_state:
        st.session_state['leaf_df'] = load_default_df()
    return st.session_state['leaf_df']

def set_leaf_df(df):
    st.session_state['leaf_df'] = df.reset_index(drop=True)

def reset_leaf_df():
    st.session_state['leaf_df'] = load_default_df()
