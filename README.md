a command line interface which takes a spotify playlist and searches for the songs in youtube, then either creates or adds to an existing playlist in youtube music. made because 
i figured if i can code it why would i use a paid service? anyways, google youtube api has a quota limit, so as of right now you can only add 66 songs to a playlist. don't worry though, 
24 hours after you reach the quota limit, you can run your code again from the same playlist, starting where you left off. it is all explained in step 5.

# 1. clone the repo.

run cd music_to_music to go into the folder.



# 2. to activate a virtual environemnt so that you don't have to install everything onto your computer: (and assuming you already have python. if not, download it)

    python3 -m venv venv (if you don't have virtual environments installed, search how to install python3 venv)
    source venv/bin/activate

install all the libraries I used:

    pip3 install -r requirements.txt


# 3. create a .env file.
**3a. paste this code and _do not change the names_:**

    SPOTIPY_CLIENT_ID="your_spotify_client_id"
    SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
    SPOTIPY_REDIRECT_URI="http://127.0.0.1:9090/callback"

**where can you find this information?**

_you have to make one so that i don't give away my secrets!_

go to the spotify developer dashboard: https://developer.spotify.com/dashboard

create an app, then copy client ID and client secret and paste them in their respective spots in the .env file.

in that app’s edit settings, add the redirect URI you’ll use (e.g. http://localhost:8080/callback). 
_**the URI must exactly match what you put in .env.**_

**3b. paste this code and _do not change the names_:**

    YT_CLIENT_ID="your_youtube_client_id"
    YT_CLIENT_SECRET="your_youtube_client_secret"

**where can you find these?**

go to google cloud console and create a project.

enable youtube data api v3.

go to credentials, create credentials, oauth client, desktop app.

paste your client id to the right of YT_CLIENT_ID=

paste your client secret to the right of YT_CLIENT_SECRET=

**almost done!**

# 4. create a file called .gitignore 
paste the next two lines within it:

    .env
    .cache

this means that your private client id's and access tokens will not be published on github if you were to try to save any code (please create a branch if you're going to do so).

!!!!

# 5. to run:

assuming you're already in an active virtual environment, this is the command line format to run code in the terminal.

**python3 spotify_to_youtube.py --id spotify_playlist_id --name youtube_playlist_name --starting-track 0  --exists 0**

let's break it down:

    --id:

       when you open a spotify playlist on your browser, the link looks something like this: https://open.spotify.com/playlist/4z3b9BCQli6iSJOqndYmgg (click on the playlist, you're welcome)
   
       if you want this playlist to be copied over to youtube, you'd put **4z3b9BCQli6iSJOqndYmgg** instead of spotify_playlist_id

**python3 spotify_to_youtube.py --id 4z3b9BCQli6iSJOqndYmgg --name youtube_playlist_name**

    --name:

        if you were to run this code, it would create a youtube playlist called youtube_playlist_name. let's name it test

**python3 spotify_to_youtube.py --id 4z3b9BCQli6iSJOqndYmgg --name test --starting-track 0**

    --starting-track:

        currently, it's starting on the first track (index 0). 
  
        if you want to start it on the 68th track, for instance, you would instead put 67 (because index starts at 0 :) )

**python3 spotify_to_youtube.py --id 4z3b9BCQli6iSJOqndYmgg --name test --starting-track 67 --exists 0**

    --exists:
  
        if you want to add to an already existing youtube playlist, the name would have to be the same, and you'd set exists to be 1

**python3 spotify_to_youtube.py --id 4z3b9BCQli6iSJOqndYmgg --name already_exists --starting-track 67 --exists 1**

This line of code will start on the 68th song from the spotify playlist specified and add to an existing youtube music playlist called already_exists.

  
  

