import dbus.service
import subprocess
import ffmpeg
from fractions import Fraction
from overrides import override
from media import Media
from audio import AudioProperties  
import os
from interface_names import MEDIA_INTERFACE, AUDIO_INTERFACE, VIDEO_INTERFACE
from app_version import VERSION

class Video(Media):
    def __init__(self, bus, object_path, file_path):
        interfaces = [MEDIA_INTERFACE, VIDEO_INTERFACE, AUDIO_INTERFACE]
        super().__init__(bus, object_path, file_path, interfaces, 'Video')
        
        self._audio = self._AudioOfVideo(file_path) 
        self.dimensions, self.frame_rate = self.extract_video_properties()
        self.interface_name = VIDEO_INTERFACE

    @dbus.service.method(VIDEO_INTERFACE, in_signature='', out_signature='b')
    def ExtractAudio(self):
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        output_path = os.path.join(os.path.dirname(self.file_path), f"{base_name}_audio.mp3")
        
        try:
            subprocess.run(['ffmpeg', '-i', self.file_path, '-q:a', '0', '-map', 'a', output_path], check=True)
            print(f"Extracted audio from {self.file_path} to {output_path}")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to extract audio from {self.file_path}")
            return False
            
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
        if interface_name == VIDEO_INTERFACE:
            return [
                {'name': 'Dimensions', 'type': '(ii)', 'access': 'read'},
                {'name': 'FrameRate', 'type': 'd', 'access': 'read'}
            ]
        elif interface_name == AUDIO_INTERFACE:
            return self._audio.get_audio_property_names()
        elif interface_name == MEDIA_INTERFACE:
            return super().GetDBusProperties(interface_name)
        return []

    @override
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")
        if interface_name == VIDEO_INTERFACE:
            if property_name == 'Dimensions':
                return dbus.Struct(self.dimensions, signature='ii')
            elif property_name == 'FrameRate':
                return dbus.Double(self.frame_rate)
        elif interface_name == AUDIO_INTERFACE:
            ret = self._audio.get_audio_property_values(property_name)
            if ret:
                return ret
        elif interface_name == MEDIA_INTERFACE:
            return super().Get(interface_name, property_name)
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                f'No such property {property_name}')