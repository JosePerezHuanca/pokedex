#importar todo
import wx
import requests
import json
import os
from getData import updatePokemonData

class SearchDialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(SearchDialog, self).__init__(parent, *args, **kw)
        self.parent = parent
        self.panel = wx.Panel(self)
        caja = wx.BoxSizer(wx.VERTICAL)

        self.searchLabel = wx.StaticText(self.panel, label='Buscar Pokemon:')
        caja.Add(self.searchLabel, 0, wx.ALL, 5)
        self.searchText = wx.TextCtrl(self.panel)
        self.searchText.Bind(wx.EVT_TEXT, self.searchPokemon)
        self.searchText.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        caja.Add(self.searchText, 0, wx.ALL, 5)

        self.resultsList = wx.ListCtrl(self.panel, style=wx.LC_SINGLE_SEL | wx.LC_REPORT)
        self.resultsList.InsertColumn(0, 'id')
        self.resultsList.InsertColumn(1, 'pokemon')
        self.resultsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        caja.Add(self.resultsList, 0, wx.ALL, 5)

        self.infoButton = wx.Button(self.panel, label='Info Pokemon')
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod)
        caja.Add(self.infoButton, 0, wx.ALL, 5)

        labelInfo = wx.StaticText(self.panel, label='Info')
        caja.Add(labelInfo, 0, wx.ALL, 5)
        self.infoText = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        caja.Add(self.infoText, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(caja)
        self.urls = []
        self.pokemonsList = []
        self.search_results = []
        self.consultaMethod()

    def clear_and_generate(self, event):
        for child in self.panel.GetChildren():
            child.Destroy()

        self.searchLabel = wx.StaticText(self.panel, label='Buscar Pokemon:')
        self.searchText = wx.TextCtrl(self.panel)
        self.searchText.Bind(wx.EVT_TEXT, self.searchPokemon)
        self.searchText.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.resultsList = wx.ListCtrl(self.panel, style=wx.LC_SINGLE_SEL | wx.LC_REPORT)
        self.resultsList.InsertColumn(0, 'id')
        self.resultsList.InsertColumn(1, 'pokemon')
        self.resultsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        self.infoButton = wx.Button(self.panel, label='Info Pokemon')
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod)
        labelInfo = wx.StaticText(self.panel, label='Info')
        self.infoText = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.searchLabel, 0, wx.ALL, 5)
        sizer.Add(self.searchText, 0, wx.ALL, 5)
        sizer.Add(self.resultsList, 0, wx.ALL, 5)
        sizer.Add(self.infoButton, 0, wx.ALL, 5)
        sizer.Add(labelInfo, 0, wx.ALL, 5)
        sizer.Add(self.infoText, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizerAndFit(sizer)

        self.Layout()

    def consultaMethod(self):
        try:
            if not os.path.exists('pokemon.json'):
                updatePokemonData()
            with open('pokemon.json', 'r') as pokemonJson:
                self.pokemonsList = json.load(pokemonJson)
        except Exception as e:
            wx.MessageBox(str(e))

    def searchPokemon(self, event):
        search_query = self.searchText.GetValue().lower()
        self.search_results = [
            (i, value['name']) for i, value in enumerate(self.pokemonsList) if search_query in value['name'].lower()
        ]
        self.updateResultsList()

    def updateResultsList(self):
        self.resultsList.DeleteAllItems()
        for ids, pokemon_name in self.search_results:
            self.resultsList.InsertItem(ids, pokemon_name)

    def onKeyPress(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_RETURN:
            self.onAccept(None)
        else:
            event.Skip()

    def onItemActivated(self, event):
        selected_index = event.GetIndex()
        self.parent.listaResultados.Select(selected_index)
        self.parent.listaResultados.EnsureVisible(selected_index)
        self.EndModal(wx.ID_OK)

    def onAccept(self, event):
        if self.resultsList.GetItemCount() > 0:
            selected_index = self.resultsList.GetFirstSelected()
            self.parent.listaResultados.Select(selected_index)
            self.parent.listaResultados.EnsureVisible(selected_index)
        self.EndModal(wx.ID_OK)

    def infoMethod(self, event):
        selected_index = self.resultsList.GetFirstSelected()
        if selected_index != -1:
            urlPokemon = self.search_results[selected_index][0]
            response = requests.get(urlPokemon)
            if response.status_code == 200:
                data = response.json()
                info = f"Name: {data['name']}\nBase experience: {data['base_experience']}\n"
                abilitiesInfo = "Abilities:\n"
                for abilitie in data['abilities']:
                    abilitiesInfo += f"{abilitie['ability']['name']}\n"
                movesInfo = f"Moves:\n"
                for move in data['moves']:
                    movesInfo += f"{move['move']['name']}\n"
                statsInfo = "Stats:\n"
                for stat in data['stats']:
                    statsInfo += f"{stat['stat']['name']}: {stat['base_stat']}\n"
                typesInfo = "Type:\n"
                for type in data['types']:
                    typesInfo += f"{type['type']['name']}\n"
                fullInfo = info + "\n" + typesInfo + "\n" + abilitiesInfo + "\n" + statsInfo + "\n" + movesInfo
                self.infoText.SetValue(fullInfo)

class MainWindow(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainWindow, self).__init__(*args, **kw)
        self.panel = wx.Panel(self)
        caja = wx.BoxSizer(wx.VERTICAL)

        labelLista = wx.StaticText(self.panel, label='Pokemons')
        caja.Add(labelLista, 0, wx.ALL, 5)
        self.listaResultados = wx.ListCtrl(self.panel, style=wx.LC_SINGLE_SEL | wx.LC_REPORT)
        self.listaResultados.InsertColumn(0, 'id')
        self.listaResultados.InsertColumn(1, 'pokemon')
        self.listaResultados.Bind(wx.EVT_CONTEXT_MENU, self.showContextMenu)
        caja.Add(self.listaResultados, 0, wx.ALL, 5)

        self.infoButton = wx.Button(self.panel, label='Info pokemon')
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod)
        caja.Add(self.infoButton, 0, wx.ALL, 5)

        labelInfo = wx.StaticText(self.panel, label='Info')
        caja.Add(labelInfo, 0, wx.ALL, 5)
        self.infoText = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        caja.Add(self.infoText, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(caja)
        self.urls = []
        self.pokemonsList = []
        self.consultaMethod(None)

        # Configurar menú
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()

        # Agregar elementos al menú
        buscar_item = fileMenu.Append(wx.ID_ANY, "&Buscar\tCtrl+F", "Buscar Pokemon")
        salir_item = fileMenu.Append(wx.ID_EXIT, "&Salir\tAlt+F4", "Salir de la aplicación")

        # Asociar eventos a los elementos del menú
        self.Bind(wx.EVT_MENU, self.mostrarBuscar, buscar_item)
        self.Bind(wx.EVT_MENU, self.OnExit, salir_item)

        menubar.Append(fileMenu, "&Archivo")
        self.SetMenuBar(menubar)

        # Configurar menú contextual
        self.context_menu = wx.Menu()
        exportar_item = self.context_menu.Append(wx.ID_ANY, "&Exportar a TXT", "Exportar Pokemon a TXT")
        self.Bind(wx.EVT_MENU, self.exportarTxt, exportar_item)

    def clear_and_generate(self, event):
        for child in self.panel.GetChildren():
            child.Destroy()

        labelLista = wx.StaticText(self.panel, label='Pokemons')
        self.listaResultados = wx.ListCtrl(self.panel, style=wx.LC_SINGLE_SEL | wx.LC_REPORT)
        self.listaResultados.InsertColumn(0, 'id')
        self.listaResultados.InsertColumn(1, 'pokemon')
        self.listaResultados.Bind(wx.EVT_CONTEXT_MENU, self.showContextMenu)
        self.infoButton = wx.Button(self.panel, label='Info pokemon')
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod)
        labelInfo = wx.StaticText(self.panel, label='Info')
        self.infoText = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(labelLista, 0, wx.ALL, 5)
        sizer.Add(self.listaResultados, 0, wx.ALL, 5)
        sizer.Add(self.infoButton, 0, wx.ALL, 5)
        sizer.Add(labelInfo, 0, wx.ALL, 5)
        sizer.Add(self.infoText, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizerAndFit(sizer)

        self.Layout()

    def consultaMethod(self, event):
        try:
            if not os.path.exists('pokemon.json'):
                updatePokemonData()
            with open('pokemon.json', 'r') as pokemonJson:
                self.pokemonsList = json.load(pokemonJson)
            self.updatePokemonList()
        except Exception as e:
            wx.MessageBox(str(e))

    def updatePokemonList(self):
        self.listaResultados.DeleteAllItems()
        self.urls = []
        self.infoButton.Enable(False)
        for ids, value in enumerate(self.pokemonsList):
            self.listaResultados.InsertItem(ids, value['name'])
            self.urls.append(value['url'])
            self.infoButton.Enable(True)

    def infoMethod(self, event):
        try:
            selected = self.listaResultados.GetFirstSelected()
            if selected != -1:
                urlPokemon = self.urls[selected]
                response = requests.get(urlPokemon)
                if response.status_code == 200:
                    data = response.json()
                    info = f"Name: {data['name']}\nBase experience: {data['base_experience']}\n"
                    abilitiesInfo = "Abilities:\n"
                    for abilitie in data['abilities']:
                        abilitiesInfo += f"{abilitie['ability']['name']}\n"
                    movesInfo = f"Moves:\n"
                    for move in data['moves']:
                        movesInfo += f"{move['move']['name']}\n"
                    statsInfo = "Stats:\n"
                    for stat in data['stats']:
                        statsInfo += f"{stat['stat']['name']}: {stat['base_stat']}\n"
                    typesInfo = "Type:\n"
                    for type in data['types']:
                        typesInfo += f"{type['type']['name']}\n"
                    fullInfo = info + "\n" + typesInfo + "\n" + abilitiesInfo + "\n" + statsInfo + "\n" + movesInfo
                    self.infoText.SetValue(fullInfo)
        except Exception as e:
            wx.MessageBox(str(e))

    def mostrarBuscar(self, event):
        self.clear_and_generate(None)
        dlg = SearchDialog(self, title="Buscar Pokemon")
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Close()

    def showContextMenu(self, event):
        self.PopupMenu(self.context_menu, event.GetPosition())

    def exportarTxt(self, event):
        selected = self.listaResultados.GetFirstSelected()
        if selected != -1:
            if self.infoText.GetValue():
                nombre_archivo = f"{self.pokemonsList[selected]['name']}_info.txt"
                with open(nombre_archivo, 'w') as file:
                    file.write(self.infoText.GetValue())

app = wx.App()
mainwindow = MainWindow(None, title='Pokedex')
mainwindow.Show()
app.MainLoop()
