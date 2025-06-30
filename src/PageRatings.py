import os
import requests
import pandas as pd
import time
from tqdm import tqdm
import re
from datetime import datetime, timedelta, timezone
import pytz
import json
from io import BytesIO
from bs4 import BeautifulSoup
import logging
import streamlit as st
from stqdm import stqdm

# Configure logging
logging.basicConfig(filename='page_ratings.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


zomato_page_ratings_links={
    "HSR": "babai-tiffins-1-hsr-bangalore",
    # "HSR": "https://www.google.com/search?q=babai+tiffins+hsr+layout",
    "SJP": "babai-tiffins-sarjapur-road-bangalore",
    # "SJP":"https://www.zomato.com/bangalore/babai-tiffins-sarjapur-road-bangalore",
    "JPN": "babai-tiffins-jp-nagar-bangalore",
    # "JPN":"https://www.google.com/search?q=babai+tiffins+jp+nagar"
}

swiggy_page_ratings_links={
    "HSR": "407773",
    "SJP": "722440",
    "JPN": "825592",
}

zomato_headers = {
'authority': 'www.zomato.com',
'accept': '*/*',
'accept-language': 'en-US,en;q=0.9',
'content-type': 'application/json',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

swiggy_headers = {
'authority': 'analytics.swiggy.com',
'accept': '*/*',
'accept-language': 'en-IN,en-US;q=0.9,en;q=0.8,te;q=0.7',
'content-type': 'application/json',
'origin': 'https://www.swiggy.com',
'referer': 'https://www.swiggy.com/',
# 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': '"Windows"',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-site',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def google_page_ratings(google_client):
    def string_to_numbers(rating_num:list):
        final_list = []
        for i in rating_num:
            try:
                final_list.append(float(i))
            except:
                final_list.append(float(re.sub(r'\D', '', i)))
        return final_list
    
    url_string={
        "SJP":["https://www.google.com/search?q=babai+Tiffins+Sarjapura","Babai Tiffins, Sarjapura","₹1–200 ‧ South Indian"],
        "JPN":["https://www.google.com/search?q=babai+tiffins+jp+nagar","JP Nagar (Cloud Kitchen)","₹1–200 ‧ South Indian"],
        "HSR":[
    "https://www.google.com/search?q=babai+tiffins+hsr+layout+bangalore",
    "Babai Tiffins, HSR Layout",
    "Google reviews"
    ]
    }
    
    main_list = []

    for branch, urls in stqdm(url_string.items(),desc="GOOGLE PAGE RATINGS"):
        df_dictinoary ={}
        headers = {
            'accept': '*/*',
            'accept-language': 'en-IN,en;q=0.9',
            'cache-control': 'no-cache',
            'referer': 'https://www.google.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version-list': '"Chromium";v="130.0.6723.70", "Google Chrome";v="130.0.6723.70", "Not?A_Brand";v="99.0.0.0"',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            }

        for attempt in range(3):
            try:
                response = requests.get(urls[0], headers=headers,timeout=10)
                soup = BeautifulSoup(response.content, "html.parser")

                for i in soup.text.split(urls[1]):
                    match = None
                    text = None
                    if urls[2] in i or "₹1–200 ‧ South Indian" in i or "₹1–200 · Restaurant" in i:
                        text = i.split(urls[2])[0]
                        if branch in ["JPN","SJP"]:
                            text = i.split(urls[2])[0]
                            number_part = text.split('Google')[0].strip()
                            match = re.match(r'(\d\.\d),?([\d,]+)', number_part)
                            if match:
                                rating, rating_count = match.group(1), match.group(2)
                                rating_count = int(rating_count.replace(',',''))
                                rating_num = rating, rating_count
                    # print(string_to_numbers([span.text for span in span_elements]))
                        elif branch == 'HSR':
                            # text = i.split(urls[2])[0]
                            # text_1 = text.split('Menu')[1]
                            # if text_1:
                            #     match = re.match(r'^(\d+\.\d)(\d+)$', text_1.strip())
                            # else:
                            text = i.split("Google reviews")[0]
                            if "Menu" in text:
                                text = text.split("Menu")[1]
                                match = re.match(r'(\d\.\d),?([\d,]+)', text)
                            else:
                                match = re.match(r'(\d\.\d)\((\d+)\)', text)
                            if match:
                                rating, rating_count = match.group(1), match.group(2)
                                rating_count = int(rating_count.replace(',',''))
                                rating_num = rating, rating_count
                break
            
            except (requests.RequestException,ValueError):
                time.sleep(2)

        if rating_num:
            print(f"GOOGLE PAGE RATINGS: For {branch} - {datetime.today().date()} - attempt - {attempt} rating_num = {rating_num}")
            df_dictinoary['date'] = datetime.today().strftime("%Y-%m-%d")
            df_dictinoary['outlet_name'] = branch
            df_dictinoary['source'] = "Google"
            df_dictinoary['page_rating'] = rating_num[0]
            df_dictinoary['ratings_count'] = int(rating_num[1])
            main_list.append(df_dictinoary)
            time.sleep(2)
        else:
            print("GOOGLE PAGE RATINGS: No data even after 3 attempts.")
    if main_list:
        final_df = pd.DataFrame(main_list)
        st.dataframe(final_df)
        final_df_1 = st.data_editor(final_df)
        all_non_null = final_df.notnull().all(axis=1).all()
        if all_non_null:
            if st.button("Submit"):
                csv_buffer = BytesIO()
                final_df_1.to_csv(
                    csv_buffer,
                    index=False
                )
                csv_file_name = f"Raw_PageRatings_{datetime.now().strftime('%d%m%Y%H%S')}"
                google_client.push_data_to_blob(
                    folder_name=f'Ratings/Google/PageRatings/{csv_file_name}.csv',
                    file_path=csv_buffer.getvalue()
                )
                csv_buffer.close()
        else:
            st.error("Extraction is not completed.")
        return 200
    else:
        return 401

def swiggy_page_ratings(swiggy_urls:dict,google_client,headers:dict):
    def find_key_in_json(json_obj, key_to_find):
        results = []
        
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == key_to_find:
                    results.append(value)
                elif isinstance(value, (dict, list)):
                    results.extend(find_key_in_json(value, key_to_find))
        elif isinstance(json_obj, list):
            for item in json_obj:
                results.extend(find_key_in_json(item, key_to_find))
        
        return results
    page_ratings=[]
    for i, restaurant_id in swiggy_urls.items():
        outlet_ratings = {}
        url = f"https://www.swiggy.com/dapi/menu/pl?page-type=REGULAR_MENU&complete-menu=true&lat=17.37240&lng=78.43780&restaurantId={restaurant_id}&catalog_qa=undefined&submitAction=ENTER"
        response = requests.get(url,headers=headers,timeout=10)
        if response.status_code == 200:
            response = requests.request("GET", url, headers=headers,timeout=10)
            json_data = response.json()
            outlet_ratings = {}
            outlet_ratings['date'] = (datetime.today()+ timedelta(days=0)).date().strftime("%Y-%m-%d")
            outlet_ratings['outlet_name'] = i
            outlet_ratings['source'] = "Swiggy"
            outlet_ratings['page_rating'] = find_key_in_json(json_obj=json_data,key_to_find="avgRatingString")[0]
            outlet_ratings['ratings_count'] = find_key_in_json(json_obj=json_data,key_to_find="totalRatings")[0]
            page_ratings.append(outlet_ratings)
        else:
            raise Exception(response.text)
    df_swiggy = pd.DataFrame(page_ratings)
    df_swiggy = df_swiggy.astype(str)
    csv_buffer = BytesIO()

    df_swiggy.to_csv(
        csv_buffer,
        index=False
    )
    csv_file_name = f"Raw_PageRatings_{datetime.now().strftime('%d%m%Y%H%S')}"
    
    google_client.push_data_to_blob(
        folder_name=f'Ratings/Swiggy/PageRatings/{csv_file_name}.csv',
        file_path=csv_buffer.getvalue()
    )
    csv_buffer.close()
def get_source_ratings(rating_type:str,ratings_dict:dict,outlet_name:str):
    outlet_ratings={}
    ratings_type_dict={"DELIVERY":"Zomato","DINING":"Zomato Dine-in"}

    outlet_ratings['date'] = datetime.today().date().strftime("%Y-%m-%d")
    outlet_ratings['outlet_name'] = outlet_name
    json_data = ratings_dict[rating_type]
    outlet_ratings['source'] = ratings_type_dict[rating_type]
    outlet_ratings['page_rating'] = json_data["rating"]
    outlet_ratings['ratings_count'] = json_data["reviewCount"]

    return outlet_ratings

def zomato_page_ratings(zomato_urls:dict,google_client,headers:dict):
    page_ratings = []
    # for i, j in tqdm(zomato_page_ratings_links.items()):
    for i, j in zomato_urls.items():
        url = f"https://www.zomato.com/webroutes/getPage?page_url=/bangalore/{j}/reviews"
        
        # print(url)
        # print(headers)
        response = requests.get(url, headers=headers,timeout=10)
        customer_page_ratings = response.json()['page_data']['sections']['SECTION_BASIC_INFO']['rating_new']['ratings']
        # customer_page_ratings = json_data['page_data']['sections']['SECTION_BASIC_INFO']['rating_new']['ratings']
        for rating_type in ['DELIVERY','DINING']:
            final_dict = get_source_ratings(rating_type=rating_type,ratings_dict=customer_page_ratings,outlet_name=i)
            page_ratings.append(final_dict)
    df_zomato = pd.DataFrame(page_ratings)
    df_zomato.ratings_count = df_zomato.ratings_count.apply(lambda x: x.replace(",",'').replace("K","000"))

    csv_buffer = BytesIO()

    df_zomato.to_csv(
        csv_buffer,
        index=False
    )
    csv_file_name = f"Raw_PageRatings_{datetime.now().strftime('%d%m%Y%H%S')}"
    google_client.push_data_to_blob(
        folder_name=f'Ratings/Zomato/PageRatings/{csv_file_name}.csv',
        file_path=csv_buffer.getvalue()
    )
    csv_buffer.close()