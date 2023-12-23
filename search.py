import wx;
import requests;
import os;
import json;
from sound_manager import SoundManager;

sound_manager = SoundManager();

class SearchDialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(SearchDialog, self).__init__(parent, *args, **kw);
        self.parent = parent;
        self.panel = wx.Panel(self);
        caja = wx.BoxSizer(wx.VERTICAL);

        self.searchLabel = wx.StaticText(self.panel, label='Buscar Pokemon:');
        caja.Add(self.searchLabel, 0, wx.ALL, 5);
        self.searchText = wx.TextCtrl(self.panel);
        self.searchText.Bind(wx.EVT_TEXT, self.searchPokemon);
        self.searchText.Bind(wx.EVT_KEY_DOWN, self.onKeyPress);
        caja.Add(self.searchText, 0, wx.ALL, 5);

        self.resultsList = wx.ListCtrl(self.panel, style=wx.LC_SINGLE_SEL | wx.LC_REPORT);
        self.resultsList.InsertColumn(0, 'id');
        self.resultsList.InsertColumn(1, 'pokemon');
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self.resultsList);
        caja.Add(self.resultsList, 0, wx.ALL, 5);

        self.infoButton = wx.Button(self.panel, label='Info Pokemon');
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod);
        caja.Add(self.infoButton, 0, wx.ALL, 5);

        labelInfo = wx.StaticText(self.panel, label='Info');
        caja.Add(labelInfo, 0, wx.ALL, 5);
        self.infoText = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_DONTWRAP);
        caja.Add(self.infoText, 1, wx.EXPAND | wx.ALL, 5);

        self.panel.SetSizer(caja);
        self.urls = [];
        self.pokemonsList = [];
        self.search_results = [];
        self.consultaMethod();

    def clear_and_generate(self, event):
        for child in self.panel.GetChildren():
            child.Destroy();

        self.searchLabel = wx.StaticText(self.panel, label='Buscar Pokemon:');
        self.searchText = wx.TextCtrl(self.panel);
        self.searchText.Bind(wx.EVT_TEXT, self.searchPokemon);
        self.searchText.Bind(wx.EVT_KEY_DOWN, self.onKeyPress);
        self.resultsList = wx.ListCtrl(self.panel, style=wx.LC_SINGLE_SEL | wx.LC_REPORT);
        self.resultsList.InsertColumn(0, 'id');
        self.resultsList.InsertColumn(1, 'pokemon');
        self.resultsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated);
        self.infoButton = wx.Button(self.panel, label='Info Pokemon');
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod);
        labelInfo = wx.StaticText(self.panel, label='Info');
        self.infoText = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2);

        sizer = wx.BoxSizer(wx.VERTICAL);
        sizer.Add(self.searchLabel, 0, wx.ALL, 5);
        sizer.Add(self.searchText, 0, wx.ALL, 5);
        sizer.Add(self.resultsList, 0, wx.ALL, 5);
        sizer.Add(self.infoButton, 0, wx.ALL, 5);
        sizer.Add(labelInfo, 0, wx.ALL, 5);
        sizer.Add(self.infoText, 1, wx.EXPAND | wx.ALL, 5);
        self.panel.SetSizerAndFit(sizer);

        self.Layout();

    def consultaMethod(self):
        try:
            if not os.path.exists('pokemon.json'):
                updatePokemonData();
            with open('pokemon.json', 'r') as pokemonJson:
                self.pokemonsList = json.load(pokemonJson);
        except Exception as e:
            wx.MessageBox(str(e));

    def searchPokemon(self, event):
        search_query = self.searchText.GetValue().lower();
        self.search_results = [
            (i, value['name'], value['url']) for i, value in enumerate(self.pokemonsList) if search_query in value['name'].lower()
        ];
        self.updateResultsList();

    def updateResultsList(self):
        self.resultsList.DeleteAllItems();
        for ids, pokemon_name, url in self.search_results:
            self.resultsList.InsertItem(ids, pokemon_name);

    def onKeyPress(self, event):
        key_code = event.GetKeyCode();
        if key_code == wx.WXK_RETURN:
            self.onAccept(None);
        else:
            event.Skip();

    def onItemActivated(self, event):
        selected_index = event.GetIndex();
        self.parent.listaResultados.Select(selected_index);
        self.parent.listaResultados.EnsureVisible(selected_index);
        self.EndModal(wx.ID_OK);

    def onAccept(self, event):
        if self.resultsList.GetItemCount() > 0:
            selected_index = self.resultsList.GetFirstSelected();
            self.parent.listaResultados.Select(selected_index);
            self.parent.listaResultados.EnsureVisible(selected_index);
        self.EndModal(wx.ID_OK);
        self.parent.consultaMethod(None)

    def infoMethod(self, event):
        selected_index = self.resultsList.GetFirstSelected();
        if selected_index != -1:
            urlPokemon = self.search_results[selected_index][2];
            response = requests.get(urlPokemon);
            if response.status_code == 200:
                data = response.json();
                info = f"Name: {data['name']}\nBase experience: {data['base_experience']}\n";
                abilitiesInfo = "Abilities:\n";
                for abilitie in data['abilities']:
                    abilitiesInfo += f"{abilitie['ability']['name']}\n";
                movesInfo = f"Moves:\n";
                for move in data['moves']:
                    movesInfo += f"{move['move']['name']}\n";
                statsInfo = "Stats:\n";
                for stat in data['stats']:
                    statsInfo += f"{stat['stat']['name']}: {stat['base_stat']}\n";
                typesInfo = "Type:\n";
                for type in data['types']:
                    typesInfo += f"{type['type']['name']}\n";
                fullInfo = info + "\n" + typesInfo + "\n" + abilitiesInfo + "\n" + statsInfo + "\n" + movesInfo+ "\n";
                self.infoText.SetValue(fullInfo);

    def onItemSelected(self, event):
        sound_manager.play_select_sound();

