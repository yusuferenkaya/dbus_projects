import dbus.service
import os
import subprocess
import ffmpeg
from fractions import Fraction
from media import Media

class Video(Media):
    def __init__(self, bus, object_path, file_path):
        super().__init__(bus, object_path, file_path, 'Video')
        self.length, self.dimensions, self.frame_rate = self.extract_video_properties()

    def extract_video_properties(self):
        """Extracts length, dimensions, and frame rate using ffmpeg."""
        try:
            probe = ffmpeg.probe(self.file_path)
            video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')

            # Extract properties
            length = float(video_info['duration'])
            width = int(video_info['width'])
            height = int(video_info['height'])
            dimensions = (width, height)

            # Parse frame rate correctly, handling fractions
            if 'r_frame_rate' in video_info:
                frame_rate_str = video_info['r_frame_rate']
                frame_rate = float(Fraction(frame_rate_str))  

            return length, dimensions, frame_rate
        except Exception as e:
            print(f"Error extracting video properties: {e}")
            return 0, (0, 0), 0.0

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if interface_name == 'com.kentkart.RemoteMediaPlayer.Media.Video':
            if property_name == 'Length':
                return self.length
            elif property_name == 'Dimensions':
                return self.dimensions
            elif property_name == 'FrameRate':
                return self.frame_rate
        return super().Get(interface_name, property_name)

    @dbus.service.method('com.kentkart.RemoteMediaPlayer.Media.Video', in_signature='s', out_signature='b')
    def ExtractAudio(self, filename):
        output_path = os.path.join(os.path.dirname(self.file_path), f"{filename}.wav")
        try:
            subprocess.run(['ffmpeg', '-i', self.file_path, '-q:a', '0', '-map', 'a', output_path], check=True)
            print(f"Extracted audio from {self.file_path} to {output_path}")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to extract audio from {self.file_path}")
            return False