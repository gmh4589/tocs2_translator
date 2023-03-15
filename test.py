from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.text import markup

# Copy this method from TextInput with no changes
buildText = '''
<InputBox@MDTextField>
<TestTIWid>:
    orientation:"vertical"
    ti: ti

    InputBox:
        id: ti
        markup: True
        multiline: True
        mode: "rectangle"
        icon_right: "./data/icon/translate.png"
        size_hint: [1, .75]

    Button:
        text: "Debug"
        on_release: root.debug()
'''

Builder.load_string(buildText)

class TestTIWid(BoxLayout):
    ti = ObjectProperty()

    def debug(self):
        self.ti.text = '[b][color=#000000]Hello[/color] [color=#ff0000]world[/color][/b]'.format(self.ti.text)

class TestTI(MDApp):
    def build(self):
        ti_wid = TestTIWid()
        return ti_wid

TestTI().run()
