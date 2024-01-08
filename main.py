import wx;
import wx.lib.mixins.listctrl as listmix;
from sound_manager import SoundManager;
import requests;
import json;
import os;
from getData import updatePokemonData;
from search import SearchDialog;

# Instancia del SoundManager
sound_manager = SoundManager();
sound_manager.play_open_sound()  # Reproducir el sonido al abrir el programa

accelerator=wx.AcceleratorEntry();


class MainWindow(wx.Frame, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kw):
        super(MainWindow, self).__init__(*args, **kw);
        self.panel = wx.Panel(self);
        caja = wx.BoxSizer(wx.VERTICAL);

        labelLista = wx.StaticText(self.panel, label='Pokemons');
        caja.Add(labelLista, 0, wx.ALL, 5);
        self.listaResultados = wx.ListCtrl(self.panel, style=wx.LC_SINGLE_SEL | wx.LC_REPORT);
        self.listaResultados.InsertColumn(0, 'id');
        self.listaResultados.InsertColumn(1, 'pokemon');
        self.listaResultados.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected);
        self.listaResultados.Bind(wx.EVT_CONTEXT_MENU, self.showContextMenu);
        caja.Add(self.listaResultados, 0, wx.ALL, 5);

        caja2=wx.BoxSizer(wx.VERTICAL);

        self.infoButton = wx.Button(self.panel, label='Info pokemon');
        self.infoButton.Bind(wx.EVT_BUTTON, self.infoMethod);
        caja2.Add(self.infoButton, 0, wx.ALL | wx.Top, 5);

        labelInfo = wx.StaticText(self.panel, label='Info');
        caja2.Add(labelInfo, 0, wx.ALL, 5);
        self.infoText = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_DONTWRAP);
        caja2.Add(self.infoText, 1, wx.EXPAND | wx.ALL, 5);

        self.searchButton=wx.Button(self.panel,label='Search');
        self.searchButton.Bind(wx.EVT_BUTTON, self.mostrarBuscar);
        accelerator.Set(wx.ACCEL_CTRL,ord('F'), self.searchButton.GetId());
        self.SetAcceleratorTable(wx.AcceleratorTable([accelerator]));
        caja2.Add(self.searchButton,0,wx.ALL | wx.Bottom,5);

        self.panel.SetSizer(caja);
        self.panel.SetSizer(caja2);
        self.urls = [];
        self.pokemonsList = [];
        self.consultaMethod(None);

        
        # Configurar menú contextual
        self.context_menu = wx.Menu();
        exportar_item = self.context_menu.Append(wx.ID_ANY, "&Exportar a TXT", "Exportar Pokemon a TXT");
        self.Bind(wx.EVT_MENU, self.exportarTxt, exportar_item);


        self.Layout();

    def consultaMethod(self, event):
        try:
            if not os.path.exists('pokemon.json'):
                updatePokemonData();
            with open('pokemon.json', 'r') as pokemonJson:
                self.pokemonsList = json.load(pokemonJson);
            self.updatePokemonList();
        except Exception as e:
            wx.MessageBox(str(e));

    def updatePokemonList(self):
        self.listaResultados.DeleteAllItems();
        self.urls = [];
        self.infoButton.Enable(False);
        for ids, value in enumerate(self.pokemonsList):
            self.listaResultados.InsertItem(ids, value['name']);
            self.urls.append(value['url']);
            self.infoButton.Enable(True);

    def infoMethod(self, event):
        try:
            selected = self.listaResultados.GetFirstSelected();
            if selected != -1:
                urlPokemon = self.urls[selected];
                response = requests.get(urlPokemon);
                if response.status_code == 200:
                    data = response.json();
                    info = f"Name: {data['name']}\nId: {data['id']}\nHeight: {data['height']}\nWeight: {data['weight']}\n";
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
                    fullInfo = info + "\n" + typesInfo + "\n" + abilitiesInfo + "\n" + statsInfo + "\n" + movesInfo;
                    self.infoText.SetValue(fullInfo);
        except Exception as e:
            wx.MessageBox(str(e));

    def mostrarBuscar(self, event):
        dlg = SearchDialog(self, title="Search");
        dlg.ShowModal();
        dlg.Destroy();

    def OnExit(self, event):
        self.Close();

    def showContextMenu(self, event):
        self.PopupMenu(self.context_menu, event.GetPosition());

    def exportarTxt(self, event):
        selected = self.listaResultados.GetFirstSelected();
        if selected != -1:
            if self.infoText.GetValue():
                nombre_archivo = f"{self.pokemonsList[selected]['name']}_info.txt";
                with open(nombre_archivo, 'w') as file:
                    file.write(self.infoText.GetValue());

    def onItemSelected(self, event):
        # Reproduce el sonido al seleccionar un elemento en la lista
        sound_manager.play_select_sound();

app = wx.App();
mainwindow = MainWindow(None, title='Pokedex');
mainwindow.Show();
app.MainLoop();
