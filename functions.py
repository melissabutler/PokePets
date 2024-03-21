
import requests
from models import Pet, Pokemon, Berry, Type

import random


BASE_URL = 'https://pokeapi.co/api/v2/pokemon/'

play_phrases = [
    " jumps around you!",
    " headbutts you in a friendly way.",
    " nibbles cheekily on your fingers.",
    " chases after the stick you threw!",
    " drops a ball in your lap."
]

berries = [
    {'name':'aspear', 
     'img_url': 'https://archives.bulbagarden.net/media/upload/a/af/Dream_Aspear_Berry_Sprite.png'},
    {'name':'cheri',
      'img_url': 'https://archives.bulbagarden.net/media/upload/a/a6/Dream_Cheri_Berry_Sprite.png'},
    {'name':'chesto',
      'img_url': 'https://archives.bulbagarden.net/media/upload/7/7e/Dream_Chesto_Berry_Sprite.png'},
    {'name':'leppa',
      'img_url': 'https://archives.bulbagarden.net/media/upload/e/e2/Dream_Leppa_Berry_Sprite.png'},
    {'name':'lum',
      'img_url': 'https://archives.bulbagarden.net/media/upload/d/d3/Dream_Lum_Berry_Sprite.png'},
    {'name':'oran',
      'img_url': 'https://archives.bulbagarden.net/media/upload/0/0c/Dream_Oran_Berry_Sprite.png'},
    {'name':'pecha',
      'img_url': 'https://archives.bulbagarden.net/media/upload/6/62/Dream_Pecha_Berry_Sprite.png'},
    {'name':'persim',
      'img_url': 'https://archives.bulbagarden.net/media/upload/3/38/Dream_Persim_Berry_Sprite.png'},
    {'name':'rawst',
      'img_url': 'https://archives.bulbagarden.net/media/upload/5/59/Dream_Rawst_Berry_Sprite.png'},
    {'name':'sitrus',
      'img_url': 'https://archives.bulbagarden.net/media/upload/a/aa/Dream_Sitrus_Berry_Sprite.png'},
                    
]
types = [
    {'name': 'bug',
     'fav_berry_id': '1',
     'least_fav_berry_id': '2'},
    {'name': 'dragon',
     'fav_berry_id': '2',
     'least_fav_berry_id': '3'},
    {'name': 'electric',
     'fav_berry_id': '3',
     'least_fav_berry_id': '4'},
    {'name': 'fighting',
     'fav_berry_id': '4',
     'least_fav_berry_id': '5'},
    {'name': 'fire',
     'fav_berry_id': '5',
     'least_fav_berry_id': '6'},
    {'name': 'flying',
     'fav_berry_id': '6',
     'least_fav_berry_id': '7'},
    {'name': 'ghost',
     'fav_berry_id': '7',
     'least_fav_berry_id': '8'},
    {'name': 'grass',
     'fav_berry_id': '8',
     'least_fav_berry_id': '9'},
     {'name': 'ground',
     'fav_berry_id': '9',
     'least_fav_berry_id': '10'},
     {'name': 'ice',
     'fav_berry_id': '10',
     'least_fav_berry_id': '1'},
     {'name': 'normal',
     'fav_berry_id': '1',
     'least_fav_berry_id': '2'},
     {'name': 'poison',
     'fav_berry_id': '2',
     'least_fav_berry_id': '3'},
     {'name': 'psychic',
     'fav_berry_id': '3',
     'least_fav_berry_id': '4'},
     {'name': 'rock',
     'fav_berry_id': '4',
     'least_fav_berry_id': '5'},
     {'name': 'water',
     'fav_berry_id': '5',
     'least_fav_berry_id': '6'},
     {'name': 'fairy',
      'fav_berry_id': '6',
      'least_fav_berry_id': '7'}
]

def create_berry_db(database, berries):
    """Puts the basic berry types into the database"""

    for berry in berries:
        new_berry = Berry(
            name=berry['name'],
            img_url = berry['img_url']
        )
        database.session.add(new_berry)
        database.session.commit()

def create_type_db(database, types):
    """ Puts the basic pokemon types into the database"""
    # types = ['bug', 'dragon','electric','fighting','fire','flying','ghost','grass','ground','ice','normal','poison','psychic','rock','water']
    for type in types:
        new_type = Type(
            name = type['name'],
            fav_berry_id = type['fav_berry_id'],
            least_fav_berry_id = type['least_fav_berry_id']
        )
        database.session.add(new_type)
        database.session.commit()


def create_pokemon_db(max, database):
    """ Calls pokemon API with a range of specific ID numbers to restrict to Gen 1"""
    gen1ids = range(1, max + 1)
    for id in gen1ids:
        resp = requests.get(f'{BASE_URL}/{id}')
        data = resp.json()
        
        pokemon = Pokemon(
            id = int(data['id']),
            name = data['name'],
            sprite_url =data['sprites']['other']['official-artwork']['front_default'],
            type = data['types'][0]['type']['name']
            # weight= data['weight']
        )
        database.session.add(pokemon)
        database.session.commit()

def get_random_ids(num):
    """Call num ids from db's range of ids"""
    ids = random.sample(range(1, 150), num)
    return ids

# def populate_shop():
# time = time.localtime()
def roll_dice(max):
    return random.randrange(1, max)

def forage():
    """ Runs a randomizer to see what the forage attempt returns"""
    
    roll = roll_dice(100)

    if roll < 10:
        #### 10% chance of straight out failure ###
        return False
    else:
        berry_roll = roll_dice(10)
        return Berry.query.get_or_404(berry_roll)
    

