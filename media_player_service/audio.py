from media import Media
import dbus.service
import subprocess

class Audio(Media):
    interface_name = 'com.kentkart.RemoteMediaPlayer.Media.Audio'

    def __init__(self, bus, object_path, file_path):
        super().__init__(bus, object_path, file_path, 'Audio')
        self.sample_rate, self.channels = self.get_audio_properties(file_path)

    def get_audio_properties(self, file_path):
        try:
            command = [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0', 
                '-show_entries', 'stream=sample_rate,channels,duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', file_path
            ]
            output = subprocess.check_output(command).decode().split('\n')
            self.length = float(output[2].strip()) 
            sample_rate = int(output[0].strip())
            channels = int(output[1].strip())
            return sample_rate, channels
        except Exception as e:
            print(f"Error extracting audio properties: {e}")
            return 0, 0  

    def GetDBusProperties(self):
        return super().GetDBusProperties() + [
            {'name': 'SampleRate', 'type': 'i', 'access': 'read'},
            {'name': 'Channels', 'type': 'i', 'access': 'read'}
        ]

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")  # Debug line
        if interface_name == self.interface_name:
            if property_name == 'SampleRate':
                print(f"Returning SampleRate: {self.sample_rate}")  # Debug line
                return dbus.Int32(self.sample_rate)
            elif property_name == 'Channels':
                print(f"Returning Channels: {self.channels}")  # Debug line
                return dbus.Int32(self.channels)
        return super().Get(interface_name, property_name)