import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests

# --- 1. Spotify setup for metadata only ---
client_id = "5507bd8a83ab47abb37d0717dbafbce4"
client_secret = "af19a1f152cc494886d98f650302d3eb"

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# --- 2. Playlist tracks fetch ---
def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

playlist_id = "2ISbuVVDFcfY6iyTV2uJSQ"
playlist_tracks = get_playlist_tracks(sp, playlist_id)

# --- 3. Fetch metadata + ReccoBeats audio features ---
track_data = []

for item in playlist_tracks:
    track = item['track']
    if not track or not track.get('id'):
        continue
    track_id = track['id']
    
    # Spotify metadata
    metadata = {
        'track_id': track_id,
        'track_name': track['name'],
        'artist': ", ".join([artist['name'] for artist in track['artists']]),
        'album': track['album']['name'],
        'release_date': track['album']['release_date'],
        'popularity': track['popularity']
    }
    
    # ReccoBeats audio features
    url = f"https://reccobeats.com/v1/track/{track_id}/audio-features"
    resp = requests.get(url)
    if resp.status_code == 200:
        audio_feats = resp.json()
        metadata.update(audio_feats)
    else:
        # Fill missing features with None
        metadata.update({k: None for k in ['danceability', 'energy', 'tempo', 'loudness', 'key', 'mode']})  # add other expected keys
    
    track_data.append(metadata)

# --- 4. Build DataFrame ---
df = pd.DataFrame(track_data)
print(df.head())

# --- 5. Optional: save to CSV ---
df.to_csv("playlist_data.csv", index=False)
