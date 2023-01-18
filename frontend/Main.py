import pandas as pd
import streamlit as st
import matplotlib as plt
import viz
import plotly.express as px
import os
import requests
import plotly.io as pio
from design import head, body

API_url = 'http://127.0.0.1:8000'

st.set_page_config(
    page_title="Recommendation Model Evaluation",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded",
)


df_r = requests.get(
    url = f'{API_url}/data'
)
st.write(df_r.json())

df = pd.DataFrame(df_r.json())

head.set_title('Recommendation Model Evaluation', 'center')

st.markdown('<h3>compare table</h3>', unsafe_allow_html=True) # display_dataframe에서 실행하면 에러 남
body.display_dataframe(df, container_width=True)
st.markdown('---')
model1, model2 = st.columns(2)
    

body.compare_metric()

plot_r = requests.get(
    url = f'{API_url}/plot'
)
plotly_fig = pio.from_json(plot_r.json())
st.plotly_chart(plotly_fig)
