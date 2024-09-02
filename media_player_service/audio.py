import dbus.service
import subprocess
from media import Media

class Audio(Media):
    def __init__(self, bus, object_path, file_path):
        interfaces = ['com.kentkart.RemoteMediaPlayer.Media', 'com.kentkart.RemoteMediaPlayer.Media.Audio']
        super().__init__(bus, object_path, file_path, interfaces, 'Audio')
        self.sample_rate, self.channels = self.get_audio_properties(file_path)
        self.interface_name = 'com.kentkart.RemoteMediaPlayer.Media.Audio'  # Explicitly set interface name

    def get_audio_properties(self, file_path):
        try:
            command = [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0', 
                '-show_entries', 'stream=sample_rate,channels,duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', file_path
            ]
            output = subprocess.check_output(command).decode().split('\n')
            self.length = float(output[2].strip())  # Update length in Media class
            sample_rate = int(output[0].strip())
            channels = int(output[1].strip())
            return sample_rate, channels
        except Exception as e:
            print(f"Error extracting audio properties: {e}")
            return 0, 0  # Return default values in case of error

    def GetDBusProperties(self, interface_name):
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Audio':
            return [
                {'name': 'SampleRate', 'type': 'i', 'access': 'read'},
                {'name': 'Channels', 'type': 'i', 'access': 'read'}
            ]
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().GetDBusProperties(interface_name)
        return []

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Audio':
            if property_name == 'SampleRate':
                return dbus.Int32(self.sample_rate)
            elif property_name == 'Channels':
                return dbus.Int32(self.channels)
            elif property_name == 'Length':  # Ensure Length property is accessible if needed
                return dbus.Double(self.length)
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().Get(interface_name, property_name)
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                f'No such property {property_name}')