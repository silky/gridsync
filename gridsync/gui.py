#!/usr/bin/env python2
# vim:fileencoding=utf-8:ft=python

from __future__ import unicode_literals

import os
import sys
import time
import threading

import wx

from config import Config
from tahoe import Tahoe
from watcher import Watcher


TRAY_ICON = '../images/systray.png'
STATE = ''

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        print('tray icon up')
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.state = ''
        self.check_state()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Open', self.on_open)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def check_state(self):
        t = threading.Timer(1.0, self.check_state)
        t.setDaemon(True)
        t.start()
        global STATE
        if STATE:
            print 'STATE!'
            self.set_icon('/home/c/circle.png')
        else:
            print 'no state...'
            self.set_icon(TRAY_ICON)

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, "Gridsync")
    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'
        global STATE
        STATE = ''
    def on_open(self, event):
        print 'open'
        global STATE
        STATE = 'yeah'
        #t = threading.Thread(target=main)
        #t.start()
    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        wx.GetApp().ExitMainLoop()
        #sys.exit()

class App(wx.App):
    def OnInit(self):
        self.SetTopWindow(wx.Frame(None, -1))
        TaskBarIcon()
        return True
    def onClose(self, evt):
        self.Destroy()
        wx.GetApp().ExitMainLoop()


def main():
    config = Config()
    settings = config.load()
    tahoe_objects = []
    watcher_objects = []
    for node_name, node_settings in settings['tahoe_nodes'].items():
        t = Tahoe(os.path.join(config.config_dir, node_name), node_settings)
        tahoe_objects.append(t)
        for sync_name, sync_settings in settings['sync'].items():
            if sync_settings[0] == node_name:
                w = Watcher(t, os.path.expanduser(sync_settings[1]), sync_settings[2])
                watcher_objects.append(w)

    for t in tahoe_objects:
        t.start()
    #global STATE
    #STATE = 'yooooo'
    for w in watcher_objects:
        w.sync()
        w.start()
    #STATE = ''
    #app = App()
    #app.MainLoop()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nshutting down!')
        for w in watcher_objects:
            w.stop()
        for t in tahoe_objects:
            t.stop()
        config.save(settings)
        sys.exit()


if __name__ == "__main__":
    #if len(sys.argv) < 3:
    #    print()
    #    print("{} - synchronize local directories with Tahoe-LAFS storage grids".format(sys.argv[0]))
    #    print()
    #    print("Usage: {} <local dir> <remote URI>".format(sys.argv[0]))
    #    print()
    #else:
    #main()
    app = App()
    app.MainLoop()

