import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import os

class Media(dbus.service.Object):
    def __init__(self, bus, object_path, file_path, media_type):
        super().__init__(bus, object_path)
        self.file_path = file_path
        self.media_type = media_type

    @dbus.service.method('com.kentkart.RemoteMediaPlayer.Media', in_signature='', out_signature='b')
    def Play(self):
        print(f"Playing {self.file_path}")
        return True  # Simulate successful playback

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if property_name == 'Type':
            return self.media_type
        elif property_name == 'File':
            return self.file_path
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                'No such property {}'.format(property_name))

class RemoteMediaPlayer(dbus.service.Object):
    def __init__(self, bus, object_path):
        super().__init__(bus, object_path)
        self.bus = bus
        self._source_directories = []
        self._media_objects = {}
        self._object_id = 0

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='s', out_signature='b')
    def AddSource(self, path):
        if os.path.isdir(path):
            self._source_directories.append(path)
            self.Scan()
            return True
        return False

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='b')
    def Scan(self):
        for directory in self._source_directories:
            if os.path.exists(directory):
                for file_name in os.listdir(directory):
                    if file_name.endswith(('.wav', '.ogg', '.mp3', '.mp4')):
                        media_path = os.path.join(directory, file_name)
                        object_path = self.generate_object_path()
                        media = Media(self.bus, object_path, media_path, self.determine_media_type(file_name))
                        self._media_objects[object_path] = media
        return True

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if property_name == 'AllMedia':
            return self.GetAllMedia()
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                'No such property {}'.format(property_name))

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='as')
    def GetAllMedia(self):
        return list(self._media_objects.keys())

    def generate_object_path(self):
        self._object_id += 1
        return f"/com/kentkart/RemoteMediaPlayer/Media{self._object_id}"

    def determine_media_type(self, file_name):
        if file_name.endswith('.mp3') or file_name.endswith('.wav'):
            return 'Audio'
        elif file_name.endswith('.mp4') or file_name.endswith('.ogg'):
            return 'Video'
        return 'Unknown'

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