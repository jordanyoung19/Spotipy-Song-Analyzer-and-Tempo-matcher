import spotipy
import json
from json.decoder import JSONDecodeError


# Prints a list of all the tracks on the album as well as creates a list of 3 tuples to store songID, song name, and counter number
def displayAlbumTracks(trackList):
    songList = []
    counter = 0
    for trackInfo in trackList:
        songName = trackInfo['name']
        songID = trackInfo['id']
        songList.append( (songName, songID, counter) )
        # print song number and name
        print(str(counter) + '. ' + songName)
        counter += 1
    return songList


def getAndDisplayUserPlaylists(spotifyObject):
    userPlaylists = spotifyObject.current_user_playlists()
    playListLst = list()
    counter = 0
    print()
    for playList in userPlaylists['items']:
        playListName = userPlaylists['items'][counter]['name']
        playListID = userPlaylists['items'][counter]['id']
        playListOwnerID = userPlaylists['items'][counter]['owner']['id']
        playListLst.append( (playListName, playListID, playListOwnerID, counter) )
        # Prints playlist nane by counter number
        print(str(counter) + ". " + playListName)
        counter += 1
    print()
    return playListLst


def findSimilarTempo(spotifyObject, tempo, playListID, playListOwnerID):
    playListTracks = spotifyObject.user_playlist_tracks(playListOwnerID, playlist_id = playListID)
    tempoDict = dict()
    for song in playListTracks['items']:
        songName = song['track']['name']
        songID = song['track']['id']
        songAnalysis = spotifyObject.audio_analysis(songID)
        songTempo = songAnalysis['track']['tempo']
        tempoDict[songName] = abs(songTempo - tempo)

    # Sorts the dictionary in order of least difference of tempos
    tempoList = sorted(tempoDict.items(), key=lambda item: item[1])

    for item in tempoList[:3]:
        print("{} has a tempo difference of {}".format(item[0], item[1]))

    #print(json.dumps(playListTracks, sort_keys=True, indent=4))
