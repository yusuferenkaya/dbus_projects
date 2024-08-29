import dbus.service
import subprocess
import threading

class Media(dbus.service.Object):
    def __init__(self, bus, object_path, file_path, media_type):
        super().__init__(bus, object_path)
        self.file_path = file_path
        self.media_type = media_type

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
        
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            if property_name == 'Type':
                return self.media_type
            elif property_name == 'File':
                return self.file_path
        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                            f'No such property {property_name}')