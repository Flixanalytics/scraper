import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Custom CSS to make the layout more responsive
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")
# Function to get video data
def get_video_data(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the title
    title = soup.find('meta', {'name': 'title'})['content']
    
    # Extract the thumbnail URL
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    
    return title, thumbnail_url

# Function to update the dataset
def update_dataset(video_id, csv_file='video_data.csv'):
    # Load existing data if CSV file exists
    if os.path.exists(csv_file):
        existing_data = pd.read_csv(csv_file)
        existing_ids = set(existing_data['Video ID'].tolist())
    else:
        existing_data = pd.DataFrame(columns=['Video ID', 'Title', 'Thumbnail URL'])
        existing_ids = set()

    if video_id not in existing_ids:
        try:
            title, thumbnail_url = get_video_data(video_id)
            new_data = {'Video ID': video_id, 'Title': title, 'Thumbnail URL': thumbnail_url}
            updated_data = pd.concat([existing_data, pd.DataFrame([new_data])], ignore_index=True)
            updated_data.to_csv(csv_file, index=False)
            
            # Save the updated file to the repository
            os.system(f'git add {csv_file} && git commit -m "Update with new video ID: {video_id}" && git push')
            
            st.success(f"Video '{title}' added successfully!")
        except Exception as e:
            st.warning(f"Failed to retrieve data for {video_id}: {e}")
    else:
        st.warning(f"Video ID '{video_id}' already exists in the dataset.")

# Streamlit App
st.title("YouTube Video Data Scraper")

video_id_input = st.text_input("Enter YouTube Video ID")

if st.button("Add Video Data"):
    if video_id_input:
        update_dataset(video_id_input)
    else:
        st.warning("Please enter a valid video ID.")

# Option to download the dataset
csv_file = 'video_data.csv'
if os.path.exists(csv_file):
    with open(csv_file, 'rb') as f:
        st.download_button("Download Dataset", data=f, file_name=csv_file)

st.info("After adding new data, the dataset is automatically updated and saved.")
