# remote_media_player.py

import dbus.service
import os
from media import Media
from audio import Audio
from video import Video

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
            self.PropertiesChanged(["AllMedia", "SourceDirectories"])  # Emitting a signal when properties change
            return True
        return False

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='b')
    def Scan(self):
        for directory in self._source_directories:
            if os.path.exists(directory):
                for file_name in os.listdir(directory):
                    media_path = os.path.join(directory, file_name)
                    object_path = self.generate_object_path()
                    if file_name.endswith(('.wav', '.mp3')):
                        media = Audio(self.bus, object_path, media_path)
                    elif file_name.endswith(('.mp4', '.ogg')):
                        media = Video(self.bus, object_path, media_path)
                    self._media_objects[object_path] = media
        return True

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='b')
    def ResetMedia(self):
        try:
            # Unregistering all media objects from DBus
            for object_path, media_object in self._media_objects.items():
                media_object.remove_from_connection()
            # Clearing the dictionary for media objects
            self._media_objects.clear()
            
            # Emitting a signal to indicate that AllMedia is changed
            self.PropertiesChanged(["AllMedia"])

            print("All media have been reset and unregistered from DBus.")
            return True
        except Exception as e:
            print(f"Failed to reset media: {e}")
            return False

    @dbus.service.signal('com.kentkart.RemoteMediaPlayer', signature='as')
    def PropertiesChanged(self, properties):
        print(f"Properties changed: {properties}")

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if property_name == 'AllMedia':
            return self.GetAllMedia()
        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                            'No such property {}'.format(property_name))

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='as')
    def GetAllMedia(self):
        if not self._media_objects:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.NoMedia',
                                                'No media available')
        return list(self._media_objects.keys())

    def generate_object_path(self):
        self._object_id += 1
        return f"/com/kentkart/RemoteMediaPlayer/Media{self._object_id}"