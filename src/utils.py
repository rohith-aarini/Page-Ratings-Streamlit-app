from datetime import datetime
import os
import streamlit as st
import traceback

from src.PageRatings import google_page_ratings, swiggy_headers, swiggy_page_ratings,swiggy_page_ratings_links
from src.PageRatings import zomato_headers, zomato_page_ratings_links, zomato_page_ratings

def create_grid_with_checkboxes(gcs,sources:list):

    # Functions to be executed
    def google_extraction():
        try:
            result = google_page_ratings(
                google_client=gcs
            )

            if result==200:
                st.success(f"PAGE RATINGS - Google page ratings extracted for {datetime.today().date().strftime('%Y-%m-%d')}")
            else:
                st.error(f"PAGE RATINGS - Google page ratings failed.")
        except Exception as e:
            st.error(traceback.print_exc())

    def swiggy_extraction():
        try:
            swiggy_page_ratings(
                swiggy_urls=swiggy_page_ratings_links,
                google_client=gcs,
                headers=swiggy_headers
            )
            st.success(f"PAGE RATINGS - Swiggy page ratings extracted for {datetime.today().date().strftime('%Y-%m-%d')}")
        except Exception as e:
            st.error(e)

    def zomato_extraction():
        try:
            zomato_page_ratings(
                zomato_urls=zomato_page_ratings_links,
                google_client=gcs,
                headers=zomato_headers
            )
            print(1+2,"Zomato")
            st.success(f"PAGE RATINGS - Zomato page ratings extracted for {datetime.today().date().strftime('%Y-%m-%d')}")
        except Exception as e:
            st.error(e)

    # Mapping between checkbox label and function
    function_dict = {
        'Google': google_extraction,
        'Swiggy': swiggy_extraction,
        'Zomato': zomato_extraction
    }
    for source in sources:
        function_dict[source]()