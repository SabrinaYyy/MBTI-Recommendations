import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import time
import base64
from requests import post, get
import os


os.environ["SPOTIPY_CLIENT_ID"] = "76403c8b967246e9ad27d55095eae39b"
os.environ["SPOTIPY_CLIENT_SECRET"] = "f83fe46ec9cf4f55a17f203dceafa4e6"


# Set up spotipy with your credentials



def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return{"Authorization": "Brearer " + token}

def search_songs_by_genre(genre):

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    print(sp.queue())
    recommendations = sp.recommendations(seed_genres=[genre], limit=10)
    print(recommendations)
    songs = []
    for track in recommendations['tracks']:
        song_info = {
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'preview_url': track['preview_url']
        }
        songs.append(song_info)

    return songs


mbtis = ['INTP','ISTP','ENTP','ESTP','ENFP','INFP','ESFP','ISFP',
        'INTJ','ISTJ','INFJ','ISFJ','ENTJ','ENFJ','ESTJ','ESFJ']
#token = get_token()


for mbti in mbtis:
    mbti_genre_file = f"{mbti} matched_genres.json"

    # Loop through each MBTI genre file
    with open(mbti_genre_file, 'r') as file:
        mbti_genre_data = json.load(file)

        # Get recommendations for each MBTI genre
        for genre in mbti_genre_data:
            print(genre)
            song_result = search_songs_by_genre(genre)

            #recommendations = sp.recommendations(seed_genres=[genre], limit=10)
            print(song_result)  # Fixed typo
            time.sleep(1) 

            # Save recommendations to a JSON file for each MBTI type and genre
            filename = f'recommendations_{mbti}_{genre.replace(" ", "_")}.json'
            with open(filename, 'a') as rec_file:
                json.dump(song_result, rec_file)
            
