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
def create_youtube_playlist(youtube, title):
    request_body = {
        "snippet": {
            "title": title,
            "description": "Transferred from Spotify"
        },
        "status": {
            "privacyStatus": "private"
        }
    }
    try:
        response = youtube.playlists().insert(
            part="snippet,status",
            body=request_body
        ).execute()
    except Exception as e:
        if e.resp.status == 403:
            if count == 0:
                print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")   
            else:
                print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")          
        exit()

    return response["id"]

#finds the playlist id in the library already and returns it
def find_existing_playlist(youtube, playlist_name):
    try:
        response = youtube.playlists().list(
            part="snippet,contentDetails",
            maxResults=10000,
            mine=True
        ).execute()
    except Exception as e:
        if e.resp.status == 403:
            if count == 0:
                print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")   
            else:
                print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")  
            exit()
        print("error")
        exit()
    
    items = response.get("items", [])
    if not items:
        return None
    for item in items:
        title = item["snippet"]["title"]
        if title.lower() == playlist_name.lower():
            return item["id"]   
    

# Search for song on YouTube and return video ID
def search_youtube_video(youtube, query):
    try:
        response = youtube.search().list(
            part="snippet",
            q=query,
            maxResults=1,
            type="video"
        ).execute()
    except Exception as e:
        if e.resp.status == 403:
            if count == 0:
                print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")   
            else:
                print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")  
            exit()
        print("error")
        exit()

    items = response.get("items", [])
    if not items:
        return None
    return items[0]["id"]["videoId"]



# Add video to YouTube playlist
def add_video_to_playlist(youtube, id, video_id):
    reps = 0
    while reps!= 20:
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
        except Exception as e:
            if e.resp.status == 403:
                if count == 0:
                    print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")   
                else:
                    print(f"Reached end of quota. Number of songs added is {count} so next time running start on track {on_song}.")   
                exit()
            print(f"Retry for {video_id} due to error.")
            reps+=1;
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
    results = sp.playlist_tracks(id, offset=start)
    tracks = []
    num_items=0
    items = results["items"]
    for item in items:
        num_items +=1
        track = item["track"]
        if track is None:
            continue;
        name = track["name"]
        artist = track["artists"][0]["name"]
        tracks.append(f"{name} {artist}")
    # if num_items < on_song:
    #     print("error: the starting track you selected doesn't exist in this playlist")
    #     exit()
    return tracks, num_items

# globals
count = 0
on_song = 0

def main():
    global count
    global on_song
    #parse arguments into variables
    parser = argparse.ArgumentParser(description="Transfer Spotify playlist to YouTube Music")
    parser.add_argument("--id", required=True, help="Spotify Playlist ID")
    parser.add_argument("--name", required=True, help="New YouTube Playlist Name")
    parser.add_argument("--starting-track", required=True, help="Track to start at")
    parser.add_argument("--exists", required=False, help="1 if you want to add to an existing playlist on youtube")
    args = parser.parse_args()

    on_song = int(args.starting_track)


    youtube = get_youtube_service()

    if args.exists == "1": #1 if im saying add to existing playlist
        id = find_existing_playlist(youtube, args.name)
        print(f"Found Youtube playlist: {args.name}")
    else:
        print(f"Creating YouTube playlist: {args.name} starting on track {args.starting_track}.")
        id = create_youtube_playlist(youtube, args.name)   

    tracks = get_spotify_tracks(args.id, int(args.starting_track))
    for track in tracks[0]:
        video_id = search_youtube_video(youtube, track)
        if video_id:
            add_video_to_playlist(youtube, id, video_id)
            print(f"Added: {track}")
            count += 1
            on_song += 1
        else:
            print(f"Not found: {track}")

    # print(f"Transfer complete! Number of songs added is {count} so next time running start on track {on_song}.")
    print(f"Transfer complete! Number of songs added is {count}!")

if __name__ == "__main__":
    main()