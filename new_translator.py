# -*- coding:utf-8 -*-
import os
import shutil
import webbrowser

import openpyxl
import configparser

from datetime import datetime

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen

from tkinter import filedialog as fd
from tkinter import messagebox as mb

setting = configparser.ConfigParser()
setting.read('setting.ini')

autosave = int(setting['Main']['autosave'])
backup = int(setting['Main']['backup'])
translator = setting['Main']['translator']

try:
    lastPath = setting['Main']['path']
except KeyError: lastPath = os.environ['USERPROFILE'] + '/Desktop'

# Загружает конфиг интерфейса
Builder.load_file('new_translator.kv')

class Colors:
    r = float(setting['Color']['r']) if float(setting['Color']['r']) <= 1 else 1/255 * int(setting['Color']['r'])
    g = float(setting['Color']['g']) if float(setting['Color']['g']) <= 1 else 1/255 * int(setting['Color']['g'])
    b = float(setting['Color']['b']) if float(setting['Color']['b']) <= 1 else 1/255 * int(setting['Color']['b'])
    a = float(setting['Color']['a']) if float(setting['Color']['a']) <= 1 else 1/255 * int(setting['Color']['a'])

    print(r, g, b, a)

class MainScreen(Screen, Colors):

    values = []
    filename = ''
    sheet = ''
    readData = ''
    sss = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, .1)
        Clock.schedule_interval(self.autoSave, autosave)
        Clock.schedule_interval(self.backups, backup)

    def fileOpen(self):

        filetypes = (
            ('Файлы Excel', '*.xlsx'),
            ('All files', '*.*')
        )

        self.filename = fd.askopenfilename(
            title = 'Выберите XLSX файл',
            initialdir = lastPath,
            filetypes = filetypes)

        if self.filename != '':

            print(self.filename)
            fName = self.filename.split('/')[-1]
            setting.set('Main', 'path', self.filename.replace(fName, ''))

            with open('setting.ini', "w") as config_file:
                setting.write(config_file)

            self.readData = openpyxl.load_workbook(self.filename, data_only = True)
            self.sheet = self.readData.active
            rows = self.sheet.max_row
            cols = self.sheet.max_column

            p = 0
            for row in range(1, rows):
                n = int((100/rows) * row)
                if n != p and n % 10 == 0: print(f'ЗАГРУЗКА {n}%...')
                p = n
                for col in range(1, cols):
                    cell = self.sheet.cell(row = row, column = col).value

                    if cell == 'dialog':
                        val = [self.sheet.cell(row = row + 1, column = col).value, '', row + 1, col]
                        self.values.append(val)

            print('ФАЙЛ ЗАГРУЖЕН!')
            self.upd()

            print(self.values)

    def writeFile(self, auto = 0):

        if self.filename != '':
            for cell in range(len(self.values)):
                o = 1 if self.values[cell][1] != '' else 0
                self.sheet.cell(row = int(self.values[cell][2]),
                                column = int(self.values[cell][3])).value = self.values[cell][o]

            self.readData.save(self.filename)
            now = datetime.now().strftime('%d.%m.%Y %H-%M-%S')
            if auto == 0:
                Factory.SavedPopup().open()
            else:
                if autosave != 0: print(f'{now} - Автосохренение выполнено!')

    def createBackup(self):

        if self.filename != '':
            now = datetime.now().strftime('%d.%m.%Y %H-%M-%S')
            name = self.filename.split('/')[-1].split('.')[0]
            shutil.copyfile(self.filename, f'backups/{name}.{now}.xlsx')
            print(f'{now} - Бекап создан!')

    def autoSave(self, dt):
        if self.filename != '' and autosave != 0: self.writeFile(1)

    def backups(self, dt):
        if self.filename != '' and backup != 0: self.createBackup()

    def nextString(self, step = '+'):

        def getHead(t):
            i = 0

            t = t.replace("'", '')

            for i in range(len(t)):
                if t[i] == '.':
                    i += 1
                    break
                if t[i].isalpha():
                    if t[i].islower(): break
            else:
                if t[-1] == 'I' or t[-1] == 'A': i = 0

            n = (i - 1)
            if "(" in t: n -= 1
            return n

        old = self.values[self.sss][0].split(' ')[0]
        h = getHead(old.split(' ')[0])
        head = old.split(' ')[0][:h]
        self.values[self.sss][1] = head + self.ids['newTXT'].text
        print(self.values[self.sss][1])

        try:
            if step == '+': self.sss += 1
            elif step == '-':
                if self.sss != 0: self.sss -= 1
                else: Factory.EOFPopup().open()
            else: self.sss = int(step)

            o = 1 if self.values[self.sss][1] != '' else 0

            ttt = str(self.values[self.sss][o])

            hText = ttt.split(' ')[0]
            if hText[0] == '#': head = getHead(hText)
            else: head = 0
            self.ids['newTXT'].text = ttt.replace(hText[:head], '')
            self.ids['originalTXT'].text = ttt

        except IndexError: Factory.EOFPopup().open()
        print(self.values)

    def update(self, dt):
        try:
            self.ids['originalTXT'].text = str(self.values[self.sss][0])
            self.ids['rdyLabel'].text = str(self.sss + 1) + '/' + str(len(self.values)) + ' готово'
            self.ids['longLabel'].text = str(len(self.values[self.sss][0])) + ' символов'
            percent = round(100 / len(self.values) * (self.sss + 1), 2)
            self.ids['percentLabel'].text = str(percent) + ' %'
            self.ids['progressBar'].value = percent

        except IndexError: pass

    def reFresh(self):
        self.ids['newTXT'].text = self.ids['originalTXT'].text

    def findBTN(self):

        text4find = str(self.ids['text4find'].text)
        text4replace = str(self.ids['text4replace'].text)
        count = 0

        for st in range(len(self.values)):
            o = 1 if self.values[st][1] != '' else 0
            if self.values[st][o].find(text4find) != -1:
                self.values[st][1] = self.values[st][o].replace(text4find, text4replace)
                if st == self.sss: self.upd()
                count += 1

        mb.showinfo(title = 'Сообщение', message = f'Выполнено {str(count)} замен')
        print(self.values)

    def upd(self):
        try:
            if str(self.values[self.sss][1]) == '':
                self.ids['newTXT'].text = str(self.values[self.sss][0])
            else:
                self.ids['newTXT'].text = str(self.values[self.sss][1])
        except IndexError: mb.showinfo(title = 'Сообщение', message = 'В файле не найдено текста для перевода!')

    def gotoBTN(self):
        try:
            goto = int(self.ids['gotoInput'].text)
            if goto < len(self.values) + 1: self.nextString(goto - 1)
            else: mb.showinfo(title = 'Сообщение', message = f'Вы ввели {goto}, а в файле только {len(self.values)} строк!')
        except (TypeError, ValueError): mb.showinfo(title = 'Сообщение', message = f'Введите число от 1 до {len(self.values)}!')

    def translate(self):

        if setting['Main']['translator'] == 'Yandex': site = 'https://translate.yandex.ru/?utm_source=main_stripe_big&lang=en-ru&text='
        elif setting['Main']['translator'] == 'Google': site = 'https://translate.google.ru/?hl=ru&tab=rT&sl=en&tl=ru&text='
        elif setting['Main']['translator'] == 'Bing': site = 'https://www.bing.com/translator/?text='
        elif setting['Main']['translator'] == 'DeepL': site = 'https://www.deepl.com/translator#en/ru/'
        elif setting['Main']['translator'] == 'Promt': site = 'https://www.translate.ru/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4/%D0%B0%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9?text='
        else: site = ''

        t = self.ids['newTXT'].text.replace('#', '')
        if t != '' and site != '': webbrowser.open(site + t)

class SettingScreen(Screen, Colors):

    tl = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids['autoSavePeriod'].text = str(autosave)
        self.ids['backupPeriod'].text = str(backup)

        self.ids[translator].state = 'down'



    def checkboxClick(self, tl1): self.tl = tl1

    def setSetting(self):

        setting.set('Main', 'autosave', self.ids['autoSavePeriod'].text)
        setting.set('Main', 'backup', self.ids['backupPeriod'].text)
        setting.set('Main', 'translator', self.tl)

        h = self.ids['colorPicker'].hex_color[1:]

        setting.set('Color', 'r', str(int(h[:2], 16)))
        setting.set('Color', 'g', str(int(h[2:4], 16)))
        setting.set('Color', 'b', str(int(h[4:6], 16)))
        setting.set('Color', 'a', str(int(h[6:], 16)))

        with open('setting.ini', "w") as config_file:
            setting.write(config_file)

        self.manager.current = 'main'

class NewTranslatorApp(App):

    # Создаёт интерфейс
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name = 'main'))
        sm.add_widget(SettingScreen(name = 'setting'))

        return sm

NewTranslatorApp().run()
