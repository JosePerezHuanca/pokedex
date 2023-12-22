import requests;
import json;
url = 'https://pokeapi.co/api/v2/pokemon/';
pokemonList=[];


def updatePokemonData():
    response = requests.get(url);
    data = response.json();

    while data['next']:
        for pokemon in data['results']:
            pokemonList.append(pokemon);
        response = requests.get(data['next']);
        data = response.json();

    for pokemon in data['results']:
        pokemonList.append(pokemon);

    with open('pokemon.json','w') as pokemonJson:
        json.dump(pokemonList, pokemonJson, indent=2);

