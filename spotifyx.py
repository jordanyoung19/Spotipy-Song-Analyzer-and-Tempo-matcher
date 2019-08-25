import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import spotifyHelper

# Get the username from terminal
username = sys.argv[1]

# User ID: j_young19?si=P6QunO_PR5G4JwCiARO64Q

# Erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username,
    client_id='enter client id here',
    client_secret='enter client secret here',
    redirect_uri='http://google.com/')
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token_(username,
    client_id='enter client id here',
    client_secret='enter client secret here',
    redirect_uri='http://google.com/')

# Create our spotifyObject
spotifyObject = spotipy.Spotify(auth=token)

user = spotifyObject.current_user()
# print(json.dumps(user, sort_keys=True, indent=4))

displayName = user['display_name']
followers = user['followers']['total']

while True:

    print()
    print(">>> Welcome to Spotipy " + displayName + "!")
    print(">>> You have " + str(followers) + " followers.")
    print()
    print("0 - search for an artist")
    print("1 - Analyze a song from an album")
    print("2 - Find similar songs to one from a playlist")
    print("3 - exit")
    print()

    # Takes user choice and ensures is valid selection
    choiceList = ['0', '1', '2', '3']
    choice = input("Your choice: ")
    if choice not in choiceList:
        print("Invalid choice selection.")
        continue


    # Search for an artist
    if choice == '0':
        print()
        searchQuery = input("Ok, what is the artist name: ")
        print()

        # Get search results
        searchResults = spotifyObject.search(searchQuery,1,0,"artist")
        print(json.dumps(searchResults, sort_keys=True, indent=4))

        # Artist Details
        artist = searchResults['artists']['items'][0]
        print(artist['name'])
        print(str(artist['followers']['total']) + ' followers')
        print(artist['genres'][0])
        print()
        webbrowser.open(artist['images'][0]['url'])
        artistID = artist['id']

        # Album and track Details
        trackURIs = []
        trackArt = []
        z = 0

        # Extract Album Data
        albumResults = spotifyObject.artist_albums(artistID, limit=10)
        albumResults = albumResults['items']

        for item in albumResults:
            print("Album " + item['name'])
            albumID = item['id']
            albumArt = item['images'][0]['url']

            # Extract track Data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']

            for item in trackResults:
                print(str(z) + ': ' + item['name'])
                trackURIs.append(item['uri'])
                trackArt.append(albumArt)
                z += 1
            print()

        # See the album art
        while True:
            songSelection = input("Enter a song number to see the album art associated with it (x to exit)")
            if songSelection == 'x':
                break
            webbrowser.open(trackArt[int(songSelection)])

    # Track analysis: exciting!!!
    if choice == '1':
        while True:
            # Search for an album
            print()
            searchQuery = input('Which album would you like to search for? (Enter 0 to exit): ')
            if searchQuery == '0':
                break
            print()

            # Retrieve album information here
            searchResults = spotifyObject.search(searchQuery,1,0,"album")
            # print(json.dumps(searchResults, sort_keys=True, indent=4))
            try:
                artistName = searchResults['albums']['items'][0]['artists'][0]['name']
                albumName = searchResults['albums']['items'][0]['name']
                confirm = input("Is " + albumName +' by ' + artistName + ' the correct album?: ')
            except:
                print("Error retrieving album information.")
                continue

            # Check to ensure correct album was searched
            if confirm == 'yes' or confirm == 'Yes':
                pass
            else:
                continue

            albumInfo = searchResults['albums']['items'][0]
            albumID = albumInfo['id']
            album = spotifyObject.album(albumID)

            # create aray of songs from the albums
            # print(json.dumps(album, sort_keys=True, indent=4))

            # Song list stores a list of 3 tuples, each containg (song name, song ID, and number)
            songList = []
            counter = 0
            albumTracks = album['tracks']['items']
            for trackInfo in albumTracks:
                songName = trackInfo['name']
                songID = trackInfo['id']
                songList.append( (songName, songID, counter) )
                # print song number and name
                print(str(counter) + '. ' + songName)
                counter += 1
            print()

            # Asks user to select track to analyze
            while True:
                trackSelect = int(input('Which track would you like to analyze?: '))
                if trackSelect < 0 or trackSelect > (len(songList)-1):
                    print("Invalid track selection.")
                    continue
                else:
                    trackID = songList[trackSelect][1]
                    break

            # Set up song analysis objects
            songAnalysis = spotifyObject.audio_analysis(trackID)
            featureAnalysis = spotifyObject.audio_features(trackID)

            # Retrieve select information for song analysis
            songKey = songAnalysis['track']['key']
            songTempo = songAnalysis['track']['tempo']
            songTimeSignature = songAnalysis['track']['time_signature']
            songDanceability = featureAnalysis[0]['danceability']
            songLiveness = featureAnalysis[0]['liveness']
            songEnergy = featureAnalysis[0]['energy']

            # Print song analysis data
            print()
            print("The song " + songList[trackSelect][0] + " by " + artistName + " is analyzed below: ")
            print()
            print("Key: " + str(songKey))
            print("Tempo: " + str(songTempo))
            print("Time Signature: " + str(songTimeSignature))
            print("Danceability: " + str(songDanceability))
            print("Liveliness: " + str(songLiveness))
            print("Energy: " + str(songEnergy))


    # Find somgs closest in tempo from playlist in comparison to single song.
    if choice == '2':
        # Beginning of this code exact same as first part of option 1 to select a single song.
        print()
        searchQuery = input('Which album would you like to search for? (Enter 0 to exit): ')
        if searchQuery == '0':
            break
        print()

        # Retrieve album information here
        searchResults = spotifyObject.search(searchQuery,1,0,"album")
        # print(json.dumps(searchResults, sort_keys=True, indent=4))
        try:
            artistName = searchResults['albums']['items'][0]['artists'][0]['name']
            albumName = searchResults['albums']['items'][0]['name']
            confirm = input("Is " + albumName +' by ' + artistName + ' the correct album?: \n')
        except:
            print("Error retrieving album information.")
            continue

        # Check to ensure correct album was searched
        if confirm == 'yes' or confirm == 'Yes':
            pass
        else:
            continue

        albumInfo = searchResults['albums']['items'][0]
        albumID = albumInfo['id']
        album = spotifyObject.album(albumID)

        # create aray of songs from the albums
        # print(json.dumps(album, sort_keys=True, indent=4))

        # Song list stores a list of 3 tuples, each containg (song name, song ID, and number)
        albumTracks = album['tracks']['items']
        songList = spotifyHelper.displayAlbumTracks(albumTracks)

        # Asks user to select track to analyze
        while True:
            trackSelect = int(input('Which track would you like to select to be cross analyzed?: '))
            if trackSelect < 0 or trackSelect > (len(songList)-1):
                print("Invalid track selection.")
                continue
            else:
                trackID = songList[trackSelect][1]
                break

        # Set up song analysis objects
        songAnalysis = spotifyObject.audio_analysis(trackID)
        featureAnalysis = spotifyObject.audio_features(trackID)

        # Retrieve select information for song analysis
        songKey = songAnalysis['track']['key']
        songTempo = songAnalysis['track']['tempo']
        songTimeSignature = songAnalysis['track']['time_signature']
        songDanceability = featureAnalysis[0]['danceability']
        songLiveness = featureAnalysis[0]['liveness']
        songEnergy = featureAnalysis[0]['energy']

        print()
        # Displays all user playlists and creates list of all playlists
        playListLst = spotifyHelper.getAndDisplayUserPlaylists(spotifyObject)

        # Grabs user selection of playList
        userChoice = int(input("Which playlist would you like to cross analyze?: "))
        # playListLst.append( (playListName, playListID, playListOwnerID, counter) )
        selectedPlayListName = playListLst[userChoice][0]
        selectedPlaylistID = playListLst[userChoice][1]
        selectedPlayListOwnerID = playListLst[userChoice][2]

        print("\nCross Analyzing, please wait.\n")

        spotifyHelper.findSimilarTempo(spotifyObject, 100, selectedPlaylistID, selectedPlayListOwnerID)





    # End the program
    if choice == '3':
        break

# print(json.dumps(VARIABLE, sort_keys=True, indent=4))
