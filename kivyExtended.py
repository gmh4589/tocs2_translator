
from kivy.compat import string_types
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label

Builder.load_file('kivyExtended.kv')

class Tooltip(Label): pass

class ToolTipButton(Button):
    tooltip_txt = StringProperty('')
    tooltip_cls = ObjectProperty(Tooltip)

    def __init__(self, **kwargs):
        self._tooltip = None
        super(ToolTipButton, self).__init__(**kwargs)
        fbind = self.fbind
        fbind('tooltip_cls', self._build_tooltip)
        fbind('tooltip_txt', self._update_tooltip)
        Window.bind(mouse_pos = self.on_mouse_pos)
        self._build_tooltip()

    def _build_tooltip(self, *largs):

        if self._tooltip: self._tooltip = None

        cls = self.tooltip_cls

        if isinstance(cls, string_types):
            cls = Factory.get(cls)

        self._tooltip = cls()
        self._update_tooltip()

    def _update_tooltip(self, *largs):
        txt = self.tooltip_txt

        if txt: self._tooltip.text = txt
        else: self._tooltip.text = ''

    def on_mouse_pos(self, *args):

        if not self.get_root_window(): return

        pos = args[1]

        sizeX = self._tooltip.size[0]
        sizeY = self._tooltip.size[1]

        posX = pos[0] - sizeX if pos[0] + sizeX > Window.size[0] else pos[0]
        posY = pos[1] - sizeY if pos[1] + sizeY > Window.size[1] else pos[1]

        self._tooltip.pos = (posX, posY)
        Clock.unschedule(self.display_tooltip)
        self.close_tooltip()

        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 1)

    def close_tooltip(self, *args): Window.remove_widget(self._tooltip)

    def display_tooltip(self, *args): Window.add_widget(self._tooltip)

