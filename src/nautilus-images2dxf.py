#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of nautilus-images2dxf
#
# Copyright (C) 2012-2016 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Nautilus', '3.0')
    gi.require_version('GExiv2', '0.10')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GExiv2
from gi.repository import Nautilus as FileManager
from images2dxfutils import images2dxfapi
import os
from threading import Thread
from urllib import unquote_plus
import mimetypes
import images2dxfutils
from images2dxfutils import sdxf
import utm

APP = '$APP$'
VERSION = '$VERSION$'

_ = str


class IdleObject(GObject.GObject):
    """
    Override GObject.GObject to always emit signals in the main thread
    by emmitting on an idle handler
    """
    def __init__(self):
        GObject.GObject.__init__(self)

    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)


class DoItInBackground(IdleObject, Thread):
    __gsignals__ = {
        'started': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (int,)),
        'ended': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (bool,)),
        'start_one': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'end_one': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (float,)),
    }

    def __init__(self, output_filename, elements):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.elements = elements
        self.output_filename = output_filename
        self.stopit = False
        self.ok = True
        self.daemon = True
        self.process = None

    def stop(self, *args):
        self.stopit = True
        if self.process is not None:
            self.process.terminate()

    def run(self):
        total = 0
        for element in self.elements:
            total += get_duration(element)
        self.emit('started', total)
        try:
            total = 0
            drawing = images2dxfutils.sdxf.Drawing()
            for element in self.elements:
                if self.stopit is True:
                    self.ok = False
                    break
                self.emit('start_one', element)
                if os.path.exists(element) and os.path.isfile(element):
                    filename = os.path.basename(element)
                    exif = GExiv2.Metadata(element)
                    coordinates = exif.get_gps_info()
                    x, y, h, lt = utm.from_latlon(coordinates[1],
                                                  coordinates[0])
                    drawing.append(sdxf.Circle(center=(x, y, 0),
                                   radius=0.5, color=3))
                    drawing.append(sdxf.Text(filename, point=(x, y, 0)))
                self.emit('end_one', get_duration(element))
            print(1)
            drawing.saveas(self.output_filename)
            print(2)
        except Exception as e:
            print(e)
            self.ok = False
        try:
            if self.process is not None:
                self.process.terminate()
                self.process = None
        except Exception as e:
            print(e)
        print('finished')
        self.emit('ended', self.ok)


class Progreso(Gtk.Dialog, IdleObject):
    __gsignals__ = {
        'i-want-stop': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, title, parent):
        Gtk.Dialog.__init__(self, title, parent,
                            Gtk.DialogFlags.MODAL |
                            Gtk.DialogFlags.DESTROY_WITH_PARENT)
        IdleObject.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(330, 30)
        self.set_resizable(False)
        self.connect('destroy', self.close)
        self.set_modal(True)
        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)
        self.get_content_area().add(vbox)
        #
        frame1 = Gtk.Frame()
        vbox.pack_start(frame1, True, True, 0)
        table = Gtk.Table(2, 2, False)
        frame1.add(table)
        #
        self.label = Gtk.Label()
        table.attach(self.label, 0, 2, 0, 1,
                     xpadding=5,
                     ypadding=5,
                     xoptions=Gtk.AttachOptions.SHRINK,
                     yoptions=Gtk.AttachOptions.EXPAND)
        #
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_size_request(300, 0)
        table.attach(self.progressbar, 0, 1, 1, 2,
                     xpadding=5,
                     ypadding=5,
                     xoptions=Gtk.AttachOptions.SHRINK,
                     yoptions=Gtk.AttachOptions.EXPAND)
        button_stop = Gtk.Button()
        button_stop.set_size_request(40, 40)
        button_stop.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_STOP, Gtk.IconSize.BUTTON))
        button_stop.connect('clicked', self.on_button_stop_clicked)
        table.attach(button_stop, 1, 2, 1, 2,
                     xpadding=5,
                     ypadding=5,
                     xoptions=Gtk.AttachOptions.SHRINK)
        self.stop = False
        self.show_all()
        self.value = 0.0

    def set_max_value(self, anobject, max_value):
        self.max_value = float(max_value)

    def get_stop(self):
        return self.stop

    def on_button_stop_clicked(self, widget):
        self.stop = True
        self.emit('i-want-stop')

    def close(self, *args):
        self.destroy()

    def increase(self, anobject, value):
        self.value += float(value)
        fraction = self.value/self.max_value
        self.progressbar.set_fraction(fraction)
        if self.value >= self.max_value:
            self.hide()

    def set_element(self, anobject, element):
        self.label.set_text(_('Converting: %s') % element)


def get_files(files_in):
    files = []
    for file_in in files_in:
        print(file_in)
        file_in = unquote_plus(file_in.get_uri()[7:])
        if os.path.isfile(file_in):
            files.append(file_in)
    return files


def get_duration(file_in):
    return os.path.getsize(file_in)


def select_output_filename(window):
    output_filename = None
    dialog = Gtk.FileChooserDialog('Select dxf output file',
                                   window,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL,
                                    Gtk.ResponseType.REJECT,
                                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    filter = Gtk.FileFilter()
    filter.set_name('dxf file')
    filter.add_mime_type('application/dxf')
    dialog.add_filter(filter)
    if dialog.run() == Gtk.ResponseType.ACCEPT:
        dialog.hide()
        output_filename = dialog.get_filename()
        if not output_filename.endswith('.dxf'):
            output_filename += '.dxf'
    dialog.destroy()
    return output_filename


class Images2dxfCreatorMenuProvider(GObject.GObject, FileManager.MenuProvider):
    """
    Implements the 'Replace in Filenames' extension to the File Manager\
    right-click menu
    """

    def __init__(self):
        """
        File Manager crashes if a plugin doesn't implement the __init__\
        method
        """
        mimetypes.init()
        pass

    def all_are_jpeg_files(self, items):
        for item in items:
            file_in = unquote_plus(item.get_uri()[7:])
            if not os.path.isfile(file_in):
                return False
            mimetype = mimetypes.guess_type('file://' + file_in)[0]
            if mimetype != 'image/jpeg':
                return False
        return True

    def convert(self, menu, selected, window):
        output_filename = select_output_filename(window)
        if output_filename is not None:
            files = get_files(selected)
            diib = DoItInBackground(output_filename, files)
            progreso = Progreso(_('Creating dxf'), window)
            diib.connect('started', progreso.set_max_value)
            diib.connect('start_one', progreso.set_element)
            diib.connect('end_one', progreso.increase)
            diib.connect('ended', progreso.close)
            progreso.connect('i-want-stop', diib.stop)
            diib.start()
            progreso.run()

    def get_file_items(self, window, sel_items):
        """
        Adds the 'Replace in Filenames' menu item to the File Manager\
        right-click menu, connects its 'activate' signal to the 'run'\
        method passing the selected Directory/File
        """
        if self.all_are_jpeg_files(sel_items):
            top_menuitem = FileManager.MenuItem(
                name='Images2dxfCreatorMenuProvider::Gtk-images2dxf-top',
                label=_('Create dxf from images'),
                tip=_('Tool to create a dxf from jpeg images'))
            submenu = FileManager.Menu()
            top_menuitem.set_submenu(submenu)

            sub_menuitem_00 = FileManager.MenuItem(
                name='Images2dxfCreatorMenuProvider::Gtk-images2dxf-sub-01',
                label=_('Create dxf'),
                tip=_('Tool to create a dxf from jpeg images'))
            sub_menuitem_00.connect('activate',
                                    self.convert,
                                    sel_items,
                                    window)
            submenu.append_item(sub_menuitem_00)
            sub_menuitem_01 = FileManager.MenuItem(
                name='Images2dxfCreatorMenuProvider::Gtk-images2dxf-sub-02',
                label=_('About'),
                tip=_('About'))
            sub_menuitem_01.connect('activate', self.about, window)
            submenu.append_item(sub_menuitem_01)
            #
            return top_menuitem,
        return

    def about(self, widget, window):
        ad = Gtk.AboutDialog(parent=window)
        ad.set_name(APP)
        ad.set_version(VERSION)
        ad.set_copyright('Copyrignt (c) 2017\nLorenzo Carbonell')
        ad.set_comments(APP)
        ad.set_license('''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
''')
        ad.set_website('http://www.atareao.es')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_documenters([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_icon_name(APP)
        ad.set_logo_icon_name(APP)
        ad.run()
        ad.destroy()


if __name__ == '__main__':
    import time
    import glob
    output_filename = select_output_filename(None)
    if output_filename is not None:
        files = glob.glob('~/Escritorio/FOTOS/*.jpg')
        print(files)
        # files = get_files(selected)
        diib = DoItInBackground(output_filename, files)
        progreso = Progreso(_('Creating dxf'), None)
        diib.connect('started', progreso.set_max_value)
        diib.connect('start_one', progreso.set_element)
        diib.connect('end_one', progreso.increase)
        diib.connect('ended', progreso.close)
        progreso.connect('i-want-stop', diib.stop)
        diib.start()
        progreso.run()
        time.sleep(5)
