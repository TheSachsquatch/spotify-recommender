import pandas as pd
import requests
import psycopg2
import sqlalchemy as db
from boto.s3.connection import S3Connection

ID = ""
secret = ""
try:
    s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])
    ID= s3.api_key
    secret = s3.secret
except:
    import src.config as config
    ID = config.api_key
    secret = config.secret_key

AUTH_URL = 'https://accounts.spotify.com/api/token'

auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials', 
    'client_id': ID, 
    'client_secret': secret,
})

auth_response_data= auth_response.json()
access_token = auth_response_data['access_token']

headers = {
    'Authorization' : 'Bearer {token}'.format(token = access_token)
}
BASE_URL = 'https://api.spotify.com/v1/'

def dataset(genre):
    artist_name = []
    track_name = []
    track_id = []
    energy = []
    instrumentalness = []
    acousticness = []
    loudness = []
    liveness = []
    tempo = []
    key = []
    valence = []
    danceability = []
    mode = []
    speechiness = []

    for i in range(0,50,50):
        results = requests.get(BASE_URL + 'search?' + 'q=genre:' + genre +'&type=track', 
                                headers=headers, params= {'include_groups': 'track', 'limit' : 50, 'offset' :i})
        results= results.json()
        for i,t in enumerate(results['tracks']['items']):
            artist_name.append(t['artists'][0]['name'])
            track_name.append(t['name'])
            track_id.append(t['id'])
            audio = requests.get(BASE_URL + 'audio-features?ids=' + t['id'],
                                headers=headers)
            audio=audio.json()
            audio = audio['audio_features'][0]
            acousticness.append(audio['acousticness'])
            energy.append(audio['energy'])
            key.append(audio['key'])
            loudness.append(audio['loudness'])
            instrumentalness.append(audio['instrumentalness'])
            liveness.append(audio['liveness'])
            tempo.append(audio['tempo'])
            valence.append(audio['valence'])
            danceability.append(audio['danceability'])
            mode.append(audio['mode'])
            speechiness.append(audio['speechiness'])

    track_dataframe = pd.DataFrame({'artist_name' : artist_name,'track_name': track_name, 
                                    'track_id': track_id, 'energy' :energy,
                                    'acousticness': acousticness, 'loudness' :loudness, 'liveness' : liveness, 
                                    'tempo' : tempo, 'key': key, 'valence' : valence, 
                                    'instrumentalness': instrumentalness, 'danceability' : danceability, 'mode' : mode,
                                'speechiness': speechiness})
    engine = db.create_engine('postgresql+psycopg2://sachinvijayaraj@localhost/music_recommender')
    track_dataframe.to_sql(genre, engine, if_exists='replace', index = False)
    return track_dataframe

def song(song_input):
    song_result = requests.get(BASE_URL + 'search?' + 'q=track:'+ song_input +'&type=track', 
                            headers=headers, params ={'include_groups': 'track', 'limit':1})
    song_result= song_result.json()
    song_result = song_result['tracks']['items'][0]
    song_id= song_result['id']

    audio_features = requests.get(BASE_URL + 'audio-features?ids=' + song_id,
                                headers=headers)
    audio_features= audio_features.json()
    aud= audio_features['audio_features'][0]
    song_features = pd.DataFrame({'energy': aud['energy'], 'acousticness': aud['acousticness'],'loudness': aud['loudness'], 'liveness' : aud['liveness'], 
                        'tempo': aud['tempo'], 'key': aud['key'] , 'valence': aud['valence']
                                , 'instrumentalness': aud['instrumentalness'], 'danceability': aud['danceability'], 
                                'mode': aud['mode'], 'speechiness': aud['speechiness']}, index=[0])
    return song_features

def suggest(song_input):
    titles = []
    artists = []
    imgs = []
    ids = []
    song_result = requests.get(BASE_URL + 'search?' + 'q=track:'+ song_input +'&type=track', 
                                headers=headers, params ={'include_groups': 'track', 'limit':5})
    song_result = song_result.json()

    for i,t in enumerate(song_result['tracks']['items']):
        titles.append(t['name'])
        artist = t['album']['artists'][0]['name']
        artists.append(artist)
        imgs.append(t['album']['images'][0]['url'])
        ids.append(t['id'])

    suggest_info = pd.DataFrame({'Artists': artists, 'Images': imgs, 'Titles':titles, 'SongID': ids})
    return suggest_info

def song_from_id(id):
    song_result = requests.get(BASE_URL +'tracks/' +id, headers=headers)
    song_result= song_result.json()
    song= song_result['name']
    return song

def genre_from_id(id):
    song_result = requests.get(BASE_URL +'tracks/' +id, headers=headers)
    song_result = song_result.json()
    artist = song_result['artists'][0]['id']
    gr = requests.get(BASE_URL +"artists/"+artist, headers=headers)
    gr = gr.json()
    gr=gr['genres'][0]
    return gr

