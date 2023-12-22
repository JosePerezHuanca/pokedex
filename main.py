import wx
import wx.lib.mixins.listctrl as listmix
from sound_manager import SoundManager
import requests
import json
import os
from getData import updatePokemonData
from search import SearchDialog

# Instancia del SoundManager
sound_manager = SoundManager()
sound_manager.play_open_sound()  # Reproducir el sonido al abrir el programa

class MainWindow(wx.Frame, listmix.ListCtrlAutoWidthMixin):
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

        # Configurar eventos de la lista para reproducción de sonido al seleccionar
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self.listaResultados)

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
        dlg = SearchDialog(self, title="Buscar Pokemon");
        dlg.ShowModal();
        dlg.Destroy();

    def OnExit(self, event):
        self.Close();

    def showContextMenu(self, event):
        self.PopupMenu(self.context_menu, event.GetPosition());

    def exportarTxt(self, event):
        selected = self.listaResultados.GetFirstSelected()
        if selected != -1:
            if self.infoText.GetValue():
                nombre_archivo = f"{self.pokemonsList[selected]['name']}_info.txt"
                with open(nombre_archivo, 'w') as file:
                    file.write(self.infoText.GetValue())

    def onItemSelected(self, event):
        # Reproduce el sonido al seleccionar un elemento en la lista
        sound_manager.play_select_sound()

app = wx.App()
mainwindow = MainWindow(None, title='Pokedex')
mainwindow.Show()
app.MainLoop()
