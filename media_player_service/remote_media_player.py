import dbus.service
import os
from media import Media
from audio import Audio
from video import Video

MY_INTERFACE = 'com.kentkart.RemoteMediaPlayer'

class RemoteMediaPlayer(dbus.service.Object):
    def __init__(self, bus, object_path):
        super().__init__(bus, object_path)
        self.bus = bus
        self._source_directories = []
        self._media_objects = {}
        self._object_id = 0
        self.version = "1.0"

    @dbus.service.method(MY_INTERFACE, in_signature='s', out_signature='b')
    def AddSource(self, path):
        if os.path.isdir(path):
            self._source_directories.append(path)
            self.Scan()
            self.PropertiesChanged(MY_INTERFACE, {"AllMedia": self.GetAllMedia(), "SourceDirectories": self._source_directories}, [])
            return True
        return False

    @dbus.service.method(MY_INTERFACE, in_signature='', out_signature='b')
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

    @dbus.service.method(MY_INTERFACE, in_signature='', out_signature='b')
    def ResetMedia(self):
        try:
            for object_path, media_object in self._media_objects.items():
                media_object.remove_from_connection()
            self._media_objects.clear()
            self.PropertiesChanged(MY_INTERFACE, {"AllMedia": []}, [])
            print("All media have been reset and unregistered from DBus.")
            return True
        except Exception as e:
            print(f"Failed to reset media: {e}")
            return False

    # Signal method to indicate property changes
    @dbus.service.signal(dbus.PROPERTIES_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
        print(f"Properties changed: {changed_properties}")

    # Method to get properties based on the D-Bus interface
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if interface_name == MY_INTERFACE:
            if property_name == 'AllMedia':
                return list(self._media_objects.keys())
            elif property_name == 'SourceDirectories':
                return self._source_directories
            elif property_name == 'Version':
                return self.version
        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                            'No such property {}'.format(property_name))

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        if interface_name == MY_INTERFACE:
            return {
                'Version': self.version,
                'SourceDirectories': self._source_directories,
                'AllMedia': list(self._media_objects.keys())
            }
        else:
            raise dbus.exceptions.DBusException(
                'com.kentkart.UnknownInterface',
                f'The object does not implement the {interface_name} interface'
            )



    # Method to get all media objects
    @dbus.service.method(MY_INTERFACE, in_signature='', out_signature='as')
    def GetAllMedia(self):
        if not self._media_objects:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.NoMedia', 'No media available')
        return list(self._media_objects.keys())

    def generate_object_path(self):
        self._object_id += 1
        return f"/com/kentkart/RemoteMediaPlayer/Media{self._object_id}"