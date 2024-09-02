import dbus
import dbus.service
import subprocess
import threading
from custom_introspectable import CustomIntrospectable

class Media(CustomIntrospectable):
    def __init__(self, bus, object_path, file_path, media_type):
        super().__init__(bus, object_path, interface_name='com.kentkart.RemoteMediaPlayer.Media')
        self.file_path = file_path
        self.media_type = media_type
        self.length = 0 
        print(f"Media initialized with file_path: {file_path}, media_type: {media_type}")  # Debug line

    def GetDBusProperties(self):
        return [
            {'name': 'Type', 'type': 's', 'access': 'read'},
            {'name': 'File', 'type': 's', 'access': 'read'},
            {'name': 'Length', 'type': 'd', 'access': 'read'}
        ]

    @dbus.service.method('com.kentkart.RemoteMediaPlayer.Media', in_signature='', out_signature='b')
    def Play(self):
        print(f"Playing {self.file_path}")  
        try:
            threading.Thread(target=self._play_media).start()
            return True
        except Exception as e:
            print(f"Failed to initiate playback: {e}")  
            return False

    def _play_media(self):
        try:
            subprocess.run(['ffplay', '-autoexit', '-nodisp', self.file_path], check=True)
            print(f"Finished playing {self.file_path}")  
        except subprocess.CalledProcessError:
            print(f"Error during playback of {self.file_path}") 

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}") 
        if interface_name == self.interface_name:
            if property_name == 'Type':
                print(f"Returning Type: {self.media_type}")  
                return dbus.String(self.media_type)
            elif property_name == 'File':
                print(f"Returning File: {self.file_path}") 
                return dbus.String(self.file_path)
            elif property_name == 'Length':
                print(f"Returning Length: {self.length}") 
                return dbus.Double(self.length)
        print(f"Property {property_name} not found for interface {interface_name}")  
        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                            f'No such property {property_name}')