# video.py

import subprocess
from media import Media

class Video(Media):
    """
    <node>
        <interface name='com.kentkart.RemoteMediaPlayer.Media.Video'>
            <property name='Length' type='d' access='read'/>
            <property name='Dimensions' type='(ii)' access='read'/>
            <property name='FrameRate' type='d' access='read'/>
            <method name='ExtractAudio'>
                <arg type='s' name='filename' direction='in'/>
                <arg type='b' name='success' direction='out'/>
            </method>
        </interface>
    </node>
    """

    def __init__(self, file_path, length, dimensions, frame_rate):
        super().__init__(file_path)
        self._type = 'Video'
        self._length = length
        self._dimensions = dimensions
        self._frame_rate = frame_rate

    @property
    def Length(self):
        return self._length

    @property
    def Dimensions(self):
        return self._dimensions

    @property
    def FrameRate(self):
        return self._frame_rate

    def ExtractAudio(self, filename):
        try:
            cmd = ['ffmpeg', '-i', self.File, '-q:a', '0', '-map', 'a', filename]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False