import dbus.service
import subprocess
from overrides import override
from media import Media

class AudioProperties:
    def __init__(self):
        self.sample_rate = 0
        self.channels = 0
        self.audio_length = 0

    def get_audio_properties(self, file_path):
        try:
            command = [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0', 
                '-show_entries', 'stream=sample_rate,channels,duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', file_path
            ]
            output = subprocess.check_output(command).decode().split('\n')
            self.audio_length = float(output[2].strip())
            self.sample_rate = int(output[0].strip())
            self.channels = int(output[1].strip())
            return self.sample_rate, self.channels, self.audio_length
        except Exception as e:
            print(f"Error extracting audio properties: {e}")
            return 0, 0, 0

    def get_audio_property_names(self):
        return [
            {'name': 'SampleRate', 'type': 'i', 'access': 'read'},
            {'name': 'Channels', 'type': 'i', 'access': 'read'},
            {'name': 'Length', 'type': 'd', 'access': 'read'}
        ]

    def get_audio_property_values(self, property_name):
        if property_name == 'SampleRate':
            return dbus.Int32(self.sample_rate)
        elif property_name == 'Channels':
            return dbus.Int32(self.channels)

        return None

class Audio(Media, AudioProperties):
    def __init__(self, bus, object_path, file_path):
        interfaces = ['com.kentkart.RemoteMediaPlayer.Media', 'com.kentkart.RemoteMediaPlayer.Media.Audio']
        super().__init__(bus, object_path, file_path, interfaces, 'Audio')
        self.get_audio_properties(file_path)
        self.length = self.audio_length
        self.interface_name = 'com.kentkart.RemoteMediaPlayer.Media.Audio'


    @override
    def GetDBusProperties(self, interface_name):
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Audio':
            return self.get_audio_property_names()
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().GetDBusProperties(interface_name)
        
        return []

    @override
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Audio':
            if property_name == 'SampleRate':
                return dbus.Int32(self.sample_rate)
            elif property_name == 'Channels':
                return dbus.Int32(self.channels)
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().Get(interface_name, property_name)
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                f'No such property {property_name}')