import dbus.service
import os
import subprocess
import ffmpeg
from fractions import Fraction
from media import Media

class Video(Media):
    def __init__(self, bus, object_path, file_path):
        interfaces = ['com.kentkart.RemoteMediaPlayer.Media', 'com.kentkart.RemoteMediaPlayer.Media.Video']
        super().__init__(bus, object_path, file_path, interfaces, 'Video')
        self.dimensions, self.frame_rate = self.extract_video_properties()
        self.interface_name = 'com.kentkart.RemoteMediaPlayer.Media.Video'  # Explicitly set interface name

    def extract_video_properties(self):
        try:
            probe = ffmpeg.probe(self.file_path)
            video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')

            self.length = float(video_info.get('duration', 0))  # Update length in Media class
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

    def GetDBusProperties(self, interface_name):
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Video':
            return [
                {'name': 'Dimensions', 'type': '(ii)', 'access': 'read'},
                {'name': 'FrameRate', 'type': 'd', 'access': 'read'}
            ]
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().GetDBusProperties(interface_name)
        return []

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Video':
            if property_name == 'Dimensions':
                return dbus.Struct(self.dimensions, signature='ii')
            elif property_name == 'FrameRate':
                return dbus.Double(self.frame_rate)
            elif property_name == 'Length':  # Move Length property here
                return dbus.Double(self.length)
        elif interface_name == 'com.kentkart.RemoteMediaPlayer.Media':
            return super().Get(interface_name, property_name)
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                f'No such property {property_name}')