import requests;
import json;
import wx;

url = 'https://pokeapi.co/api/v2/pokemon/';
pokemonList=[];


def updatePokemonData():
    response = requests.get(url);
    data = response.json();
    total=data['count'];
    progress=wx.ProgressDialog("Actualizando datos", "Obteniendo datos de https://pokeapi.co...", maximum=total, style=wx.PD_AUTO_HIDE | wx.PD_APP_MODAL);

    while data['next']:
        for pokemon in data['results']:
            pokemonList.append(pokemon);
        (keep_going, skip) = progress.Update(len(pokemonList),newmsg=f"Procesando {len(pokemonList)} de {total} elementos");
        
        response = requests.get(data['next']);
        data = response.json();

    for pokemon in data['results']:
        pokemonList.append(pokemon);
    (keep_going, skip) = progress.Update(len(pokemonList),newmsg=f"Procesando {len(pokemonList)} de {total} elementos");

    with open('pokemon.json','w') as pokemonJson:
        json.dump(pokemonList, pokemonJson, indent=2);

