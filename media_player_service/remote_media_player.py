# remote_media_player.py

import dbus.service
from custom_introspectable import CustomIntrospectable
from overrides import override  
import os
from media import Media
from audio import Audio
from video import Video
from gi.repository import GLib  

class RemoteMediaPlayer(CustomIntrospectable):
    def __init__(self, bus, object_path):
        interfaces = ['com.kentkart.RemoteMediaPlayer']
        super().__init__(bus, object_path, interfaces)
        self.bus = bus
        self._source_directories = []
        self._media_objects = {}
        self._media_files = set()
        self._object_id = 0
        self._playing_media = set()  

        Media.event_emitter.on('media_play', self.on_media_play)
        Media.event_emitter.on('media_stop', self.on_media_stop)

    @override
    def GetDBusProperties(self, interface_name):
        """Override to provide D-Bus properties for introspection."""
        if interface_name == 'com.kentkart.RemoteMediaPlayer':
            return [
                {'name': 'Version', 'type': 's', 'access': 'read'},
                {'name': 'SourceDirectories', 'type': 'as', 'access': 'read'},
                {'name': 'AllMedia', 'type': 'ao', 'access': 'read'},
                {'name': 'PlayingMedia', 'type': 'ao', 'access': 'read'}
            ]
        return []

    @override
    def GetDBusSignals(self, interface_name):
        """Override to provide D-Bus signals for introspection."""
        if interface_name == 'com.kentkart.RemoteMediaPlayer':
            return [
                {'name': 'PropertiesChanged'},
                {'name': 'PlayingMediaChanged'}
            ]
        return []

    def on_media_play(self, media_object_path):
        """Handle media_play event."""
        self._playing_media.add(media_object_path)
        self.PlayingMediaChanged(list(self._playing_media))

    def on_media_stop(self, media_object_path):
        """Handle media_stop event."""
        self._playing_media.discard(media_object_path)
        self.PlayingMediaChanged(list(self._playing_media))

    @dbus.service.signal('com.kentkart.RemoteMediaPlayer', signature='ao')
    def PlayingMediaChanged(self, playing_media):
        print(f"Playing media changed: {playing_media}")

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='s', out_signature='b')
    def AddSource(self, path):
        if os.path.isdir(path):
            self._source_directories.append(path)
            GLib.idle_add(self.emit_properties_changed, path)
            return True
        return False

    def emit_properties_changed(self, path):
        self._scan_directory(path)
        self.PropertiesChanged(
            'com.kentkart.RemoteMediaPlayer', 
            {
                "AllMedia": dbus.Array(self.GetAllMedia(), signature='o'),
                "SourceDirectories": dbus.Array(self._source_directories, signature='s'),
                "PlayingMedia": dbus.Array(list(self._playing_media), signature='o')
            }, 
            []
        )
        return False  
        
    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='b')
    def Scan(self):
        # Resetting all media and unpublishing objects
        for object_path, media_object in list(self._media_objects.items()):
            media_object.remove_from_connection()
        self._media_objects.clear()
        self._media_files.clear()
        
        # Scan all source directories from scratch
        for directory in self._source_directories:
            self._scan_directory(directory)

        self.PropertiesChanged(
            'com.kentkart.RemoteMediaPlayer', 
            {
                "AllMedia": dbus.Array(self.GetAllMedia(), signature='o'),
                "SourceDirectories": dbus.Array(self._source_directories, signature='s'),
                "PlayingMedia": dbus.Array(list(self._playing_media), signature='o')
            }, 
            []
        )
        return True

    def _scan_directory(self, directory):
        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                media_path = os.path.join(directory, file_name)
                if media_path in self._media_files:
                    continue  # Skip already added media files
                object_path = self.generate_object_path()
                if file_name.endswith(('.wav', '.mp3')):
                    media = Audio(self.bus, object_path, media_path)  
                elif file_name.endswith(('.mp4', '.ogg')):
                    media = Video(self.bus, object_path, media_path)  
                else:
                    continue  

                self._media_objects[object_path] = media
                self._media_files.add(media_path)  

    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='b')
    def ResetMedia(self):
        try:
            for object_path, media_object in list(self._media_objects.items()):
                media_object.remove_from_connection()
            self._media_objects.clear()
            self._media_files.clear()
            
            self.PropertiesChanged(
                'com.kentkart.RemoteMediaPlayer', 
                {
                    "AllMedia": dbus.Array([], signature='o'), 
                    "SourceDirectories": dbus.Array([], signature='s'),
                    "PlayingMedia": dbus.Array([], signature='o')
                }, 
                []
            )

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
        if interface_name == 'com.kentkart.RemoteMediaPlayer':
            if property_name == 'AllMedia':
                return dbus.Array(self.GetAllMedia(), signature='o') 
            elif property_name == 'SourceDirectories':
                return dbus.Array(self._source_directories, signature='s')  
            elif property_name == 'Version':
                return dbus.String("1.0")
            elif property_name == 'PlayingMedia':
                return dbus.Array(list(self._playing_media), signature='o')
        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                            'No such property {}'.format(property_name))

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        if interface_name == 'com.kentkart.RemoteMediaPlayer':
            return {
                'AllMedia': dbus.Array(self.GetAllMedia(), signature='o'),
                'SourceDirectories': dbus.Array(self._source_directories, signature='s'),
                'Version': dbus.String("1.0"),
                'PlayingMedia': dbus.Array(list(self._playing_media), signature='o')
            }
        else:
            raise dbus.exceptions.DBusException(
                'com.example.UnknownInterface',
                'The RemoteMediaPlayer object does not implement the %s interface'
                % interface_name)

    def generate_object_path(self):
        self._object_id += 1
        return f"/com/kentkart/RemoteMediaPlayer/Media/{self._object_id}"  
    
    @dbus.service.method('com.kentkart.RemoteMediaPlayer', in_signature='', out_signature='as')
    def GetAllMedia(self):
        if not self._media_objects:
            return dbus.Array([], signature='o') 
        return list(self._media_objects.keys())