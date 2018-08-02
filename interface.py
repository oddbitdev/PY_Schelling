import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from grid_models import Column, GridLocation, Row
from tile_model import RandomTileTypeGenerator, Tile, TileSystem, TileType
from world_model import World

kivy.require('1.10.0')


Builder.load_file('interface.kv')


class MapGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MapGrid, self).__init__(**kwargs)


class ControlBar(BoxLayout):
    def __init__(self, **kwargs):
        super(ControlBar, self).__init__(**kwargs)


class InterfaceContainer(BoxLayout):
    def __init__(self, context, **kwargs):
        super(InterfaceContainer, self).__init__(**kwargs)
        self.context = context
        self.orientation = 'horizontal'

 
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)


class TileLabel(Label):
    def __init__(self, **kwargs):
        super(TileLabel, self).__init__(**kwargs)
 
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self.parent.parent.parent.parent.context.tap_label(self.text)


class Interface(App):
    def __init__(self, rows, cols, **kwargs):
        super(Interface, self).__init__(**kwargs)
        self.is_running_sim = False
        self.rows = rows
        self.cols = cols
        self.content = InterfaceContainer(context=self, orientation='vertical')
        self.world = None
        self.grid = None
        self.event = None
        self.labels = {}

    def build(self):
        return self.content

    def update_tiles(self):
        self.grid.clear_widgets()
        for r in range(self.rows):
            for c in range(self.cols):
                t: Tile = self.world.tile_system.tile_at_loc(GridLocation(Row(r), Column(c)))
                if t.tile_type.value == 1:
                    c = [1, 1, 1, 1]
                elif t.tile_type.value == 2:
                    c = [0, 1, 0, 1]
                else:
                    c = [0, 0, 1, 1]
                l = TileLabel(text=str(t.tile_id), color=c)
                self.labels['r'+str(r)+'c'+str(c)] = l
                self.grid.add_widget(l)
 
    def generate_world(self):
        self.content.ids.main_screen.clear_widgets()
        twd = {TileType.Empty: 6, TileType.Green: 3, TileType.Blue: 3}
        self.world = World(self.rows, self.cols, False, twd)
        self.grid = MapGrid(cols=self.cols, rows=self.rows)
        self.update_tiles()
        self.content.ids.main_screen.add_widget(self.grid)
 
    def run_step(self, dt=1.):
        self.world.run_step()
        self.update_tiles()

    def run_pause_sim(self):
        if self.is_running_sim:
            self.event.cancel()
            self.is_running_sim = False
        else:
            self.is_running_sim = True
            self.event = Clock.schedule_interval(self.run_step, 1.)

    def tap_label(self, lt):
        tile : Tile = self.world.tile_system.tile_by_id(int(lt))
        tile_des = self.world.tile_desirability(tile, tile.tile_type, True)
        ns  = self.world.tile_neighbours(tile)
        dm  = self.world.desirability_matrix(tile)
        t   = "Selected: " + lt + "\n"
        t  += "Tile type: " + str(tile.tile_type) + "\n"
        if tile.tile_type != TileType.Empty:
            t  += "Self derisability: " + str(tile_des) + "\n"
            t  += "Neighbours: " + str([t.tile_id for t in ns]) + "\n"
            for tpl in dm:
                t += str(tpl[0].tile_id) + ": " + str(tpl[1]) + "\n"

        self.content.ids.info_label.text = t


if __name__ == '__main__':
    Interface(24, 24).run()
