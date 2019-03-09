import json

pokedex = json.load(open('pokemon_data/pokedex.json'))


def pokemons_gen(names):
    return (pokemon for pokemon in pokedex if pokemon['ename'] in names)


def ids(names):
    return list(map(lambda pok: int(pok['id']), pokemons_gen(names)))

