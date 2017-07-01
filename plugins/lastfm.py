import requests
from tinydb import TinyDB, Query
from steelybot import config


COMMAND = '.np'
USERDB = TinyDB('../lastfm.json')
USER = Query()


def get_np(apikey, user):
    base = "http://ws.audioscrobbler.com/2.0/"
    payload = {'method': 'user.getRecentTracks',
               'user': user,
               'api_key': apikey,
               'limit': '2',
               'format': 'json'}
    response = requests.get(base, params=payload)
    return response.json()["recenttracks"]["track"][0]

def get_tags(artist, track):
    base = "http://ws.audioscrobbler.com/2.0/"
    payload = {'method': 'artist.gettoptags',
               'api_key': config.LASTFM_API_KEY,
               'artist': artist,
               'user': 'alexkraak',
               'format': 'json'}
    response = requests.get(base, params=payload).json()
    top = 0
    try:
        for tag in response['toptags']['tag']:
            if top < 3:
                top += 1
                yield tag['name']
    except KeyError:
        yield 'None'


def extract_song(user):
    try:
        response = get_np(config.LASTFM_API_KEY, user)
    except requests.exceptions.RequestException:
        return 'failed to retrieve now playing information'
    artist = response['artist']['#text']
    song = response['name']
    tags = list(get_tags(artist, song))
    return '{} is playing {} by {}. tags: {}'.format(user, song, artist, tags)


def main(bot, author_id, message, thread_id, thread_type, **kwargs):
    message_split = message.split()
    if not message:
        search = USERDB.search(USER.fb_id == author_id)
        if len(search) != 0:
            lastfm_name = search[0]['lastfm']
            bot.sendMessage(extract_song(lastfm_name),
                            thread_id=thread_id, thread_type=thread_type)
        else:
            bot.sendMessage('include username please or use .np set',
                            thread_id=thread_id, thread_type=thread_type)
        return

    elif message_split[0] == 'set' and len(message_split) == 2:
        if len(USERDB.search(USER.fb_id == author_id)) == 0:
            USERDB.insert({"fb_id": author_id, "lastfm": message_split[1]})
            bot.sendMessage('good egg',
                            thread_id=thread_id, thread_type=thread_type)
        else:
            USERDB.update({"lastfm": message_split[1]},
                          USER.fb_id == author_id)
            bot.sendMessage('updated egg',
                            thread_id=thread_id, thread_type=thread_type)
        return
    else:
        bot.sendMessage(extract_song(message),
                        thread_id=thread_id, thread_type=thread_type)
        return