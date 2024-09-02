import dbus.service
import os
import xml.etree.ElementTree as ET
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

    def Introspect(self, object_path, connection):
        xml = super(RemoteMediaPlayer, self).Introspect(object_path, connection)

        tree = ET.ElementTree(ET.fromstring(xml))
        interface_element = tree.find(".//interface[@name='com.kentkart.RemoteMediaPlayer']")
        if interface_element is not None:
            for property_name, property_type in [('Version', 's'), ('SourceDirectories', 'as'), ('AllMedia', 'ao')]:
                prop = ET.Element('property', {'name': property_name, 'type': property_type, 'access': 'read'})
                interface_element.append(prop)

        return ET.tostring(tree.getroot(), encoding='unicode')

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='s', out_signature='b')
    def AddSource(self, path):
        if os.path.isdir(path):
            self._source_directories.append(path)
            self.Scan()

            self.PropertiesChanged(MY_INTERFACE, 
                       {
                           "AllMedia": dbus.Array(self.GetAllMedia(), signature='o'),
                           "SourceDirectories": dbus.Array(self._source_directories, signature='s')
                       }, 
                       [])
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
            for object_path, media_object in self._media_objects.items():
                media_object.remove_from_connection()
            self._media_objects.clear()
            
            self.PropertiesChanged(MY_INTERFACE, {"AllMedia": dbus.Array([], signature='o'), "SourceDirectories": dbus.Array([], signature='s')}, [])

            print("All media have been reset and unregistered from DBus.")
            return True
        except Exception as e:
            print(f"Failed to reset media: {e}")
            return False

    @dbus.service.signal(dbus.PROPERTIES_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
        pass
    
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if interface_name == MY_INTERFACE:
            if property_name == 'AllMedia':
                return dbus.Array(self.GetAllMedia(), signature='o')  # Ensure empty list is returned properly
            elif property_name == 'SourceDirectories':
                return dbus.Array(self._source_directories, signature='s')  # Ensure empty list is returned properly
            elif property_name == 'Version':
                return dbus.String("1.0")
        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                            'No such property {}'.format(property_name))

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        if interface_name == MY_INTERFACE:
            return {
                'AllMedia': dbus.Array(self.GetAllMedia(), signature='o'),
                'SourceDirectories': dbus.Array(self._source_directories, signature='s'),
                'Version': dbus.String("1.0")
            }
        else:
            raise dbus.exceptions.DBusException(
                'com.example.UnknownInterface',
                'The RemoteMediaPlayer object does not implement the %s interface'
                % interface_name)

    def generate_object_path(self):
        self._object_id += 1
        return f"/com/kentkart/RemoteMediaPlayer/Media{self._object_id}"

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='as')
    def GetAllMedia(self):
        if not self._media_objects:
            return dbus.Array([], signature='o') 
        return list(self._media_objects.keys())