# audio.py

from media import Media
import dbus.service
import subprocess

class Audio(Media):
    def __init__(self, bus, object_path, file_path):
        super().__init__(bus, object_path, file_path, 'Audio')
        self.sample_rate, self.length, self.channels = self.get_audio_properties(file_path)

    def get_audio_properties(self, file_path):
        try:
            command = [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0', 
                '-show_entries', 'stream=sample_rate,channels,duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', file_path
            ]
            output = subprocess.check_output(command).decode().split('\n')
            sample_rate = int(output[0].strip())
            channels = int(output[1].strip())
            length = float(output[2].strip())
            return sample_rate, length, channels
        except Exception as e:
            print(f"Error extracting audio properties: {e}")
            return 0, 0, 0  # Return default values in case of error

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Audio':
            if property_name == 'SampleRate':
                return self.sample_rate
            elif property_name == 'Length':
                return self.length
            elif property_name == 'Channels':
                return self.channels
        return super().Get(interface_name, property_name)