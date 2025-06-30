import streamlit as st
from datetime import datetime
import pandas as pd
from io import BytesIO
from CloudStoragePush.CSDataPush import DataPush
from google.oauth2 import service_account
from google.cloud import bigquery

@st.cache_resource
def gcs_connection():
    gcs = DataPush()
    gcs.initial_connect(
        key_info=st.secrets['new_gcp_key']
    )
    gcs.get_bucket(bucket_name=st.secrets["GCS_BUCKET"])
    return gcs

@st.cache_resource
def bq_connection():
    credentials = service_account.Credentials.from_service_account_info(
        # self.KEY_PATH,
        info = st.secrets['new_gcp_key'],
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    bq_client = bigquery.Client(credentials=credentials)
    return bq_client



st.title("Babai Tiffins Page Ratings")
gcs = gcs_connection()
bq_client = bq_connection()

current_date = datetime.now().strftime('%Y-%m-%d')

st.text("Click on the below to open the corresponding page.")

cols = st.columns(3)

cols[0].link_button("SJP","https://www.google.com/search?q=babai+tiffins+sarjapur")
cols[1].link_button("HSR","https://www.google.com/search?q=babai+tiffins+hsr+layout")
cols[2].link_button("JPN","https://www.google.com/search?q=babai+tiffins+jp+nagar")

# final_df = pd.DataFrame(
#     {
#         "date":[current_date,current_date,current_date],
#         "outlet_name":['SJP',"HSR","JPN"],
#         "source":['Google','Google','Google'],
#         'page_rating':['4.4','4.4','4.3'],
#         'ratings_count':['3587','793','58'],
#      }
# )

query = """
    SELECT
    date,
    outlet_name,
    source,
    page_rating,
    ratings_count
    FROM `dev-analytics-gcp-bt.Raw.PageRatings`
    WHERE source = "Google"
    AND date = (SELECT MAX(date) FROM `dev-analytics-gcp-bt.Raw.PageRatings` WHERE source = "Google")
"""
# Execute the query
query_job = bq_client.query(query)  # API request

# Fetch results
results = query_job.result()
final_df = results.to_dataframe()

final_df['date'] = current_date

final_edited_df = st.data_editor(final_df)

file_timestamp = datetime.now().strftime('%d%m%Y%H%S')

if st.button("Submit"):
    # st.dataframe(final_edited_df)
    csv_buffer = BytesIO()
    final_edited_df.to_csv(
        csv_buffer,
        index=False
    )
    csv_file_name = f"Raw_PageRatings_{file_timestamp}"
    gcs.push_data_to_blob(
        folder_name=f'Ratings/Google/PageRatings/{csv_file_name}.csv',
        file_path=csv_buffer.getvalue()
    )
    csv_buffer.close()
    gcs.close_client()

    st.success("Page Ratings Pushed to cloud.")