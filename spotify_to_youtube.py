from dotenv import load_dotenv
import time
import os
import json
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# YouTube API Scopes
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube"]

# Authenticate YouTube and return service object
def get_youtube_service():
    flow = InstalledAppFlow.from_client_config({
        "installed": {
            "client_id": os.getenv("YT_CLIENT_ID"),
            "client_secret": os.getenv("YT_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }, scopes=YOUTUBE_SCOPES)

    credentials = flow.run_local_server(port=0)
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube

# Create playlist on YouTube
def create_youtube_playlist(youtube, title, description):
    request_body = {
        "snippet": {
            "title": title,
            "description": description
        },
        "status": {
            "privacyStatus": "private"
        }
    }

    response = youtube.playlists().insert(
        part="snippet,status",
        body=request_body
    ).execute()

    return response["id"]

# Search for song on YouTube and return video ID
def search_youtube_video(youtube, query):
    response = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=1,
        type="video"
    ).execute()

    items = response.get("items", [])
    if not items:
        return None
    return items[0]["id"]["videoId"]



# Add video to YouTube playlist
def add_video_to_playlist(youtube, id, video_id):
    count = 0
    while count!= 20:
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
            return
        except HttpError as e:
            print(f"Retry for {video_id} due to error.")
            count+=1;
            time.sleep(2)





# Get track list from Spotify playlist
def get_spotify_tracks(id, start):
    sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id = os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri = "http://127.0.0.1:8888/callback",
        scope = "user-library-read"
        )
    )
    results = sp.playlist_tracks(id)
    tracks = []
    num_items=0
    count=0
    items = results["items"]
    for item in items[start:]:
        num_items +=1
        track = item["track"]
        if track is None:
            continue;
        name = track["name"]
        artist = track["artists"][0]["name"]
        tracks.append(f"{name} {artist}")
        count += 1
    return tracks, num_items, count

# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transfer Spotify playlist to YouTube Music")
    parser.add_argument("--id", required=True, help="Spotify Playlist ID")
    parser.add_argument("--name", required=True, help="New YouTube Playlist Name")
    parser.add_argument("--starting-track", required=True, help="Track to start at")
    args = parser.parse_args()

    youtube = get_youtube_service()

    print(f"Creating YouTube playlist: {args.name} starting on track {args.starting_track}.")
    id = create_youtube_playlist(youtube, args.name, "Transferred from Spotify")

    tracks = get_spotify_tracks(args.id, int(args.starting_track))
    
    for track in tracks[0]:
        video_id = search_youtube_video(youtube, track)
        if video_id:
            add_video_to_playlist(youtube, id, video_id)
            print(f"Added: {track}")
        else:
            print(f"Not found: {track}")
    

    print(f"Transfer complete! Number of songs added is {tracks[2]}.")
