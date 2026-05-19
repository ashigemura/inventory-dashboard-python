import pandas as pd
import streamlit as st


# CSV読み込み
@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    return df