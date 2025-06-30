import os
import streamlit as st

from CloudStoragePush.CSDataPush import DataPush
from src.utils import create_grid_with_checkboxes 

@st.cache_resource
def gcs_connection():
    gcs = DataPush()
    gcs.initial_connect(
        key_info=st.secrets['new_gcp_key']
    )
    gcs.get_bucket(bucket_name=st.secrets["GCS_BUCKET"])
    return gcs

st.title('Babai Tiffins Page Ratings')
gcs = gcs_connection()
with st.form("Page Ratings",clear_on_submit=True):
    source_options = st.multiselect(label='Data Source',options=['Google','Swiggy','Zomato'])
    submitted = st.form_submit_button("Submit")

if source_options:
    create_grid_with_checkboxes(
        gcs=gcs,
        sources=source_options
    )

    # st.success(f"Success fully push data for {", ".join(source_options)}")  
