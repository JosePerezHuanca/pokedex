import wx;
import requests;
import json;
import os;
from getData import updatePokemonData;




class MainWindow(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainWindow, self).__init__(*args, **kw);
        self.panel=wx.Panel(self);
        caja=wx.BoxSizer(wx.VERTICAL);
        labelLista = wx.StaticText(self.panel, label='Pokemons');
        caja.Add(labelLista,0, wx.ALL, 5);
        self.listaResultados=wx.ListCtrl(self.panel);
        self.listaResultados.InsertColumn(0, 'id')
        self.listaResultados.InsertColumn(1, 'pokemon')
        caja.Add(self.listaResultados,0, wx.ALL, 5);
        self.infoButton=wx.Button(self.panel, label='Info pokemon');
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod);
        caja.Add(self.infoButton,0, wx.ALL, 5);
        labelInfo = wx.StaticText(self.panel, label='Info');
        caja.Add(labelInfo,0,wx.ALL,5);
        self.infoText=wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2);
        caja.Add(self.infoText, 0, wx.ALL, 5);

        self.panel.SetSizer(caja)
        self.urls=[];
        self.consultaMethod(None);


    def consultaMethod(self, event):
        try:
            if not os.path.exists('pokemon.json'):
                updatePokemonData();
            with open('pokemon.json', 'r') as pokemonJson:
                pokemonsList=json.load(pokemonJson);
            self.listaResultados.DeleteAllItems();
            self.urls=[];
            self.infoButton.Enable(False);
            for ids, value in enumerate(pokemonsList):
                self.listaResultados.InsertItem(ids, value['name']);
                self.urls.append(value['url']);
                self.infoButton.Enable(True);
        except Exception as e:
            wx.MessageBox(str(e));

    def infoMethod(self,event):
        try:
            selected=self.listaResultados.GetFirstSelected();
            if selected!= -1:
                urlPokemon=self.urls[selected];
                response=requests.get(urlPokemon);
                if (response.status_code==200):
                    data=response.json();
                    info=f"Name: {data['name']}\nBase experience: {data['base_experience']}\n";
                    abilitiesInfo= "Abilities:\n";
                    for abilitie in data['abilities']:
                        abilitiesInfo += f"{abilitie['ability']['name']}\n";
                    movesInfo=f"Moves:\n";
                    for move in data['moves']:
                        movesInfo += f"{move['move']['name']}\n";
                    statsInfo = "Stats:\n";
                    for stat in data['stats']:
                        statsInfo += f"{stat['stat']['name']}: {stat['base_stat']}\n";
                    typesInfo="Type:\n";
                    for type in data['types']:
                        typesInfo += f"{type['type']['name']}\n";
                    fullInfo= info + "\n"+ typesInfo+ "\n" +abilitiesInfo +"\n" +statsInfo+ "\n"+ movesInfo;
                    self.infoText.SetValue(fullInfo);
        except Exception as e:
            wx.MessageBox(str(e));


app=wx.App();
mainwindow=MainWindow(None, title='Pokedex');
mainwindow.Show();
app.MainLoop();
