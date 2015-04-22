#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponygui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
import binascii
import sys
try:
    # py3
    from tkinter import Label, Button, Frame, Toplevel, Menu
    from tkinter.ttk import Notebook
    from tkinter.constants import N, S, E, W, NSEW
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    from tkinter.messagebox import showerror
except ImportError:
    # py2
    from Tkinter import Label, Button, Frame, Toplevel, Menu
    from ttk import Notebook
    from Tkconstants import N, S, E, W, NSEW
    from tkFileDialog import askopenfilename, asksaveasfilename
    from tkMessageBox import showerror
from .basegui import BaseGui
from .missingponiesframe import MissingPoniesFrame
from .currenciesframe import CurrenciesFrame
from .poniesframe import PoniesFrame
from .zonesframe import ZonesFrame
from src.savemanager import (SaveManager, SaveError,
                             decompress_data, compress_data)
from src.xml.xmlhandler import XmlHandler
from src.utility.gluid import retrieve_gluid

if sys.version_info.major < 3:
    import codecs
    open = codecs.open

class LoadingDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        Label(self, text="Loading...", font=25, height=3, width=25).pack()
        self.update()


class PonyGui(BaseGui):
    def __init__(self, savefile, gluid, dbfile, usedb, legacy):
        BaseGui.__init__(self, savefile, gluid, dbfile, usedb, legacy)
        self.loaded = False
        self.withdraw()
        self._load_xml()
        if self.loaded:
            BaseGui.init(self)
            self.deiconify()
            self.update_idletasks()

    def _load_xml(self):
        loadingbox = LoadingDialog(self)
        if not self.legacy:
            gluid = retrieve_gluid(self.dbfile) if self.usedb else self.gluid
            gluid = binascii.a2b_base64(gluid)
        else:
            gluid = b''
        self._save_manager = SaveManager(self.savefile,
                                         gluid)
        try:
            data, self.save_number = self._save_manager.load(self.legacy)
            if not self.legacy:
                data = decompress_data(data)
        except Exception as e:
            showerror("Error",
                      "Was unable to load from file, reason: {}".format(str(e)))
            self.destroy()
        else:
            self.loaded = True
            self._xml_handle = XmlHandler(data)
            self._xml_handle.pre_load()
            loadingbox.destroy()

    def _unload(self):
        self.loaded = False
        self.destroy()

    def _export_xml(self):
        filename = asksaveasfilename()
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self._xml_handle.prettify())
            except Exception as e:
                showerror("Error",
                          "Was unable to write to file, reason: {}".format(str(e)))

    def _import_xml(self):
        filename = askopenfilename()
        if filename:
            try:
                loadingbox = LoadingDialog(self)
                with open(filename, 'rb') as f:
                    xml_data = f.read()
                new_xml_handle = XmlHandler(xml_data)
                new_xml_handle.pre_load()
            except Exception as e:
                showerror("Error",
                          "Was unable to load from file, reason: {}".format(str(e)))
            else:
                self._xml_handle = new_xml_handle
                self.withdraw()
                BaseGui.reinit(self)
                self.deiconify()
                self.update_idletasks()
            finally:
                loadingbox.destroy()

    def _remove_frames(self):
        BaseGui._remove_frames(self)
        self._file_frame.grid_forget()
        self._key_frame.grid_forget()
        self._notebook.grid_forget()

    def _remove_widgets(self):
        BaseGui._remove_widgets(self)
        self._save_button.grid_forget()

    def _create_widgets(self):
        BaseGui._create_widgets(self)
        self._menu = Menu(self)
        self._filemenu = Menu(self)
        self._filemenu.add_command(label="Open another file", command=self._unload)
        self._filemenu.add_separator()
        self._filemenu.add_command(label="Export XML...", command=self._export_xml)
        self._filemenu.add_command(label="Import XML...", command=self._import_xml)
        self._menu.add_cascade(label="File", menu=self._filemenu)
        # self._aboutmenu = Menu(self)
        # self._aboutmenu.add_command(label="Check for update", command=None)
        # self._aboutmenu.add_separator()
        # self._aboutmenu.add_command(label="About", command=None)
        # self._menu.add_cascade(label="About", menu=self._aboutmenu)
        self.config(menu=self._menu)

    def _create_frames(self):
        BaseGui._create_frames(self)
        self._notebook = Notebook(self)
        self._currencies_frame = CurrenciesFrame(self, self._xml_handle)
        self._zones_frame = ZonesFrame(self, self._xml_handle)
        self._ponies_frame = PoniesFrame(self, self._xml_handle)
        self._missing_ponies_frame = MissingPoniesFrame(self, self._xml_handle)
        self._notebook.add(self._currencies_frame,
                           text="Currencies")
        self._notebook.add(self._ponies_frame,
                           text="Ponies")
        self._notebook.add(self._zones_frame,
                           text="Zones")
        self._notebook.add(self._missing_ponies_frame,
                           text="Missing ponies")
        self._save_button = Button(self,
                                   text="Save to file",
                                   command=self._save)

    def _grid_frames(self):
        BaseGui._grid_frames(self)
        self._file_frame.grid(row=0, column=0, pady=5, sticky=NSEW)
        self._key_frame.grid(row=1, column=0, pady=10, sticky=NSEW)
        self._notebook.grid(row=3, column=0, sticky=NSEW)

    def _grid_widgets(self):
        BaseGui._grid_widgets(self)
        self._save_button.grid(row=2, column=0, sticky=NSEW, padx=3, pady=4)

    def _save(self):
        try:
            if not self.legacy:
                gluid = retrieve_gluid(self.dbfile) if self.usedb else self.gluid
                gluid = binascii.a2b_base64(gluid)
            else:
                gluid = b''
        except:
            showerror("Error", "Bad encryption key")
        else:
            loadingbox = LoadingDialog(self)
            try:
                self._currencies_frame.commit()
                self._ponies_frame.commit()
                self._zones_frame.commit()
                self._missing_ponies_frame.commit()
                try:
                    data = self._xml_handle.to_string().encode('utf-8')
                except UnicodeDecodeError:
                    data = self._xml_handle.to_string()
                self._save_manager.save(compress_data(data),
                                        self.savefile,
                                        self.save_number,
                                        gluid,
                                        self.legacy)
            except Exception as e:
                showerror("Error",
                          "Was unable to write to file, reason: {}".format(str(e)))
            finally:
                loadingbox.destroy()
