import dbus.service
import subprocess
import ffmpeg
from fractions import Fraction
from overrides import override
from media import Media
from audio import AudioProperties  

class Video(Media):
    def __init__(self, bus, object_path, file_path):
        interfaces = ['com.kentkart.RemoteMediaPlayer.Media', 
                      'com.kentkart.RemoteMediaPlayer.Media.Video', 
                      'com.kentkart.RemoteMediaPlayer.Media.Audio']
        super().__init__(bus, object_path, file_path, interfaces, 'Video')
        
        self._audio = self._AudioOfVideo(file_path) 
        self.dimensions, self.frame_rate = self.extract_video_properties()
        self.interface_name = 'com.kentkart.RemoteMediaPlayer.Media.Video'

    class _AudioOfVideo(AudioProperties):
        def __init__(self, file_path):
            super().__init__()  
            self.sample_rate, self.channels, self.length = self.get_audio_properties(file_path)

    def extract_video_properties(self):
        try:
            probe = ffmpeg.probe(self.file_path)
            video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
            self.length = float(video_info.get('duration', 0))
            width = int(video_info.get('width', 0))
            height = int(video_info.get('height', 0))
            dimensions = (width, height)

            frame_rate = 0.0
            if 'r_frame_rate' in video_info:
                frame_rate_str = video_info['r_frame_rate']
                frame_rate = float(Fraction(frame_rate_str))

            return dimensions, frame_rate
        except Exception as e:
            print(f"Error extracting video properties: {e}")
            return (0, 0), 0.0

    @override
    def GetDBusProperties(self, interface_name):
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Video':
            return [
                {'name': 'Dimensions', 'type': '(ii)', 'access': 'read'},
                {'name': 'FrameRate', 'type': 'd', 'access': 'read'}
            ]
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Audio':
            return self._audio.get_audio_property_names()
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().GetDBusProperties(interface_name)
        return []

    @override
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Video':
            if property_name == 'Dimensions':
                return dbus.Struct(self.dimensions, signature='ii')
            elif property_name == 'FrameRate':
                return dbus.Double(self.frame_rate)
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Audio':
            ret = self._audio.get_audio_property_values(property_name)
            if ret:
                return ret
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().Get(interface_name, property_name)
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                f'No such property {property_name}')