import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from src.data_gen import *
import psycopg2
import sqlalchemy as db
from sqlalchemy import inspect
from apiclient.discovery import build

def getRecs(genre, song_name):
    URL = ""
    try:
       full_url = os.environ['DATABASE_URL']
       URL = 'postgresql+psycopg2' +full_url[8:]
    except:
        URL = 'postgresql+psycopg2://sachinvijayaraj@localhost/music_recommender'
    full_url = os.environ['DATABASE_URL']
    URL = 'postgresql+psycopg2' +full_url[8:]
    engine = db.create_engine(URL)
    insp = inspect(engine)
    track_dataframe = pd.DataFrame()
    if genre in insp.get_table_names():
        track_dataframe = pd.read_sql(genre, engine)
    else:
        track_dataframe= dataset(genre)

    song_features = song(song_name)

    rec_features = track_dataframe[['energy', 'acousticness', 'loudness', 'liveness', 'tempo', 'key', 'valence', 
                                'instrumentalness', 'danceability', 'mode', 'speechiness']]

    scaler = MinMaxScaler()
    scaleRecs = pd.concat([song_features, rec_features])
    scaleRecs= scaler.fit_transform(scaleRecs)
    song_features = scaleRecs[0]
    sims = rec_features.copy()
    song_features = song_features.reshape(-1,11)
    sims= track_dataframe.copy()
    sims["similarity"] = cosine_similarity(rec_features, song_features)
    sims = sims.sort_values(by='similarity', ascending = False)
    first_song = suggest(song_name)
    first_song[["Artists", "Titles"]]
    first_song = first_song.rename(columns = {"Artists": "artist_name", "Titles":"track_name"})
    sims = first_song.append(sims[["artist_name", "track_name"]])
    sims = sims.reset_index()
    videos = []
    #for index,row in sims.iterrows():
        #ar = row["artist_name"]
        #tr = row["track_name"]
        #query = tr + " " + ar
        #video = youtube.search().list(q=query, part = "snippet", type = "video", maxResults = 1)
        #video = video.execute()
        #video = video['items'][0]['id']['videoId']
        #videoURL = "youtube.com/watch?v=" +video
        #videos.append(videoURL)
    #sims["videoURL"]= videos
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    sims = sims.iloc[:10]
    s=Service(ChromeDriverManager().install())
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options,service=s)
    sim_short = sims[5:]
    for i in range(5):
        videos.append("none")
    for index,row in sim_short.iterrows():
        ar = row["artist_name"]
        tr = row["track_name"]
        query = tr + " " + ar
        driver.get("https://youtube.com/results?search_query="+query)
        element =driver.find_element_by_id("video-title")
        watch = element.get_attribute("href")
        embed = "https://youtube.com/embed/" + watch[32:]
        videos.append(embed)
    sims["links"] = videos
    return sims



