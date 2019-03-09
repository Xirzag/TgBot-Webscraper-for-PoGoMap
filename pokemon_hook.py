import random
import codecs
import urllib
import urllib.parse
import urllib.request
import httplib2
import time
import json
import re
import math

http = httplib2.Http()


def timestamp(offset=0):
    return str(int(time.time() * 100 + offset))


maps = {'''urls of the target maps'''}
hide_pok = [23, 27, 46, 50, 54, 79, 90, 98, 120, 138, 140, 158, 183, 194, 223]

def_coord = {
    'latitude': 0,
    'longitude': 0,
}



user_agents = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
    'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.97 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0',
    'Mozilla/5.0 (Android 4.4; Tablet; rv:40.0) Gecko/40.0 Firefox/40.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14'
)


def get_pokemons_old(map_url, coord, reject_id_list=[]):
    base_url = re.search('^http://([\w\\.]*)/', map_url, re.IGNORECASE).group(1)
    url = map_url + '/raw_data'
    body = {'timestamp': timestamp(),
            'pokemon': 'true',
            'lastpokemon': 'true',
            'pokestops': 'true',
            'lastpokestops': 'true',
            'luredonly': 'false',
            'gyms': 'true',
            'lastgyms': 'true',
            'scanned': 'false',
            'spawnpoints': 'false',
            's2cells': 'false',
            'weatherAlerts': 'false',
            'swLat': format(coord['swLat'], '.14f'),
            'swLng': format(coord['swLng'], '.14f'),
            'neLat': format(coord['neLat'], '.14f'),
            'neLng': format(coord['neLng'], '.14f'),
            'oSwLat': format(coord['swLat'], '.14f'),
            'oSwLng': format(coord['swLng'], '.14f'),
            'oNeLat': format(coord['neLat'], '.14f'),
            'oNeLng': format(coord['neLng'], '.14f'),
            'reids': '',
            'eids': ', '.join(str(x) for x in reject_id_list),
            '_': timestamp(-100)
            }
    headers = {'Host': base_url,
               'Connection': 'keep-alive',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'X-Requested-With': 'XMLHttpRequest',
               'User-Agent': random.choice(user_agents),
               'DNT': '1',
               'Referer': map_url,
               'Accept-Encoding': map_url,
               'Accept-Language': 'es,en-GB;q=0.9,en;q=0.8',
               }

    try:
        response, content = http.request(url, 'GET', headers=headers, body=urllib.parse.urlencode(body))
        if content is not None:
            return json.loads(content.decode('utf-8'))
        else:
            return ['Error']

    except Exception:
        return ['Error']


def get_pokemons(map_url, coord, reject_id_list=[]):
    base_url = re.search('^http://([\w\\.]*)/', map_url, re.IGNORECASE).group(1)
    url = map_url + '/raw_data'
    body = {'timestamp': timestamp(),
            'pokemon': 'true',
            'lastpokemon': 'true',
            'pokestops': 'true',
            'lastpokestops': 'true',
            'luredonly': 'false',
            'gyms': 'true',
            'lastgyms': 'true',
            'scanned': 'false',
            'spawnpoints': 'false',
            's2cells': 'false',
            'weatherAlerts': 'false',
            'swLat': format(coord['swLat'], '.14f'),
            'swLng': format(coord['swLng'], '.14f'),
            'neLat': format(coord['neLat'], '.14f'),
            'neLng': format(coord['neLng'], '.14f'),
            'oSwLat': format(coord['swLat'], '.14f'),
            'oSwLng': format(coord['swLng'], '.14f'),
            'oNeLat': format(coord['neLat'], '.14f'),
            'oNeLng': format(coord['neLng'], '.14f'),
            'reids': '',
            'eids': ', '.join(str(x) for x in reject_id_list),
            '_': timestamp(-100)
            }
    headers = {'Host': base_url,
               'Connection': 'keep-alive',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'X-Requested-With': 'XMLHttpRequest',
               'User-Agent': random.choice(user_agents),
               'DNT': '1',
               'Referer': map_url,
               'Accept-Encoding': map_url,
               'Accept-Language': 'es,en-GB;q=0.9,en;q=0.8',
               }

    try:
        data = urllib.parse.urlencode(body)
        data = data.encode('ascii')
        req = urllib.request.Request(url, data, headers=headers, method='GET')
        with urllib.request.urlopen(req) as response:
            if response is None:
                return {'Error': 'Returned none'}
            else:
                '''content = response.read()
                return json.loads(content.decode('utf-8'))'''
                # reader = codecs.getreader("utf-8")
                # return json.load(reader(response))

                responseJSON = ""
                for _ in range(0, 5):
                    try:
                        responseJSONpart = response.read()
                    except http.client.IncompleteRead as icread:
                        responseJSON = responseJSON + icread.partial.decode('utf-8')
                        continue
                    else:
                        responseJSON = responseJSON + responseJSONpart.decode('utf-8')
                        break

                return json.loads(responseJSON)

    except Exception as error:
        return {'Error': repr(error)}




def int_null(n):
    return 0 if n is None else int(n)


def get_ivs(pokemon):
    return (int_null(pokemon['individual_attack']) +
            int_null(pokemon['individual_defense']) +
            int_null(pokemon['individual_stamina'])) * 100.0 / 45.0


def get_coordinates(coords, distance):
    side = distance / math.sqrt(2)
    R = 63710.0

    arc = side / R

    i = 0

    return {
        'swLat': coords['latitude'] - arc,
        'swLng': coords['longitude'] - arc,
        'neLat': coords['latitude'] + arc,
        'neLng': coords['longitude'] + arc
    }


PASS, REJECT, ACCEPT = range(3)


def filter_pokemon(pokemons, filters):
    interesting = []
    for pokemon in pokemons:
        for filter in filters:
            result = filter(pokemon)
            if result == REJECT:
                break
            elif result == ACCEPT:
                interesting.append(pokemon)
                break

    return interesting


def select_specific_pokemons(pokemons, option=ACCEPT):
    def filter(pokemon):
        return option if pokemon['pokemon_id'] in pokemons else PASS

    return filter


def find_specific_rarities(rarities=['Ultra Rare'], option=ACCEPT):
    def filter(pokemon):
        return option if pokemon['pokemon_id'] in rarities else PASS

    return filter


def filter_near_pokemons(coord):
    def filter(pokemon):
        return PASS if inside_square({'x': pokemon['latitude'], 'y': pokemon['longitude']}, coord) else REJECT

    return filter


def select_third_gen():
    def filter(pokemon):
        return ACCEPT if pokemon['pokemon_id'] >= 252 else PASS

    return filter


def is_magikarp_xl(pokemon):
    return pokemon['pokemon_name'] is 'Magikarp' and pokemon['weight'] and pokemon['weight'] >= 13.13


def select_xl_magikarp():
    def filter(pokemon):
        return ACCEPT if is_magikarp_xl(pokemon) else PASS

    return filter


def is_rattata_xs(pokemon):
    return pokemon['pokemon_name'] is 'Rattata' and pokemon['weight'] and pokemon['weight'] <= 2.41


def select_xs_rattata():
    def filter(pokemon):
        return ACCEPT if is_rattata_xs(pokemon) else PASS

    return filter


def all_option(option=ACCEPT):
    def filter(pokemon):
        return option

    return filter


def select_iv_pokemons(iv, pokemons=None):
    def filter(pokemon):
        if pokemons is not None and pokemon['pokemon_id'] not in pokemons:
            return PASS
        return ACCEPT if get_ivs(pokemon) >= iv else PASS

    return filter


def inside_square(coord, square):
    lat_ok = square['neLat'] > coord['x'] > square['swLat']
    lng_ok = square['neLng'] > coord['y'] > square['swLng']
    return lat_ok and lng_ok



pokemon_data = {}
pokemon_timestamp = 0


def try_get_pokemon(map_url, coord, reject_id_list=[]):
    global pokemon_data
    global pokemon_timestamp
    temp = get_pokemons(map_url, coord, reject_id_list)
    if 'Error' in temp:
        return temp
    pokemon_data = temp
    pokemon_timestamp = time.time()
    return pokemon_data


def get_cached_pokemons(map_url, coord, reject_id_list=[]):
    if time.time() - pokemon_timestamp > 30:
        for i in range(3):
            if 'Error' not in try_get_pokemon(map_url, coord, reject_id_list):
                return pokemon_data
            time.sleep(0.07)

        return try_get_pokemon(map_url, coord, reject_id_list)

    return pokemon_data