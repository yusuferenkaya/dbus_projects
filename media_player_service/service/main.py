# main.py

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from service.remote_media_player import RemoteMediaPlayer 


def main():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    service_name = dbus.service.BusName("com.kentkart.RemoteMediaPlayer", bus)
    remote_media_player = RemoteMediaPlayer(bus, "/com/kentkart/RemoteMediaPlayer")
    print("Remote Media Player Service is running...")
    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()