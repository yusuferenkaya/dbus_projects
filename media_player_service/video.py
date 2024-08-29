import dbus.service
import os
import subprocess
import ffmpeg
from fractions import Fraction
from media import Media

class Video(Media):
    interface_name = 'com.kentkart.RemoteMediaPlayer.Media.Video'

    def __init__(self, bus, object_path, file_path):
        super().__init__(bus, object_path, file_path, 'Video')
        self.dimensions, self.frame_rate = self.extract_video_properties()

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

    def GetDBusProperties(self):
        return super().GetDBusProperties() + [
            {'name': 'Dimensions', 'type': '(ii)', 'access': 'read'},
            {'name': 'FrameRate', 'type': 'd', 'access': 'read'}
        ]

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")  
        if interface_name == self.interface_name:
            if property_name == 'Dimensions':
                return dbus.Struct(self.dimensions)
            elif property_name == 'FrameRate':
                return dbus.Double(self.frame_rate)
        return super().Get(interface_name, property_name)