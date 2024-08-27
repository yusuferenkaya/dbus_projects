# media.py

import os

class Media:
    """
    <node>
        <interface name='com.kentkart.RemoteMediaPlayer.Media'>
            <property name='Type' type='s' access='read'/>
            <property name='File' type='s' access='read'/>
            <method name='Play'>
                <arg type='b' name='success' direction='out'/>
            </method>
        </interface>
    </node>
    """
    def __init__(self, file_path):
        self._file_path = file_path
        self._type = self.determine_type(file_path)

    @property
    def Type(self):
        return self._type

    @property
    def File(self):
        return self._file_path

    def Play(self):
        print(f"Playing {self._file_path}")
        play_command = f"play {self._file_path}" if self._type in ['WAV', 'OGG', 'MP3'] else f"play_video {self._file_path}"
        os.system(play_command)
        return True

    def determine_type(self, file_path):
        if file_path.endswith('.wav'):
            return 'WAV'
        elif file_path.endswith('.ogg'):
            return 'OGG'
        elif file_path.endswith('.mp3'):
            return 'MP3'
        elif file_path.endswith('.mp4'):
            return 'MP4'
        else:
            return 'Unknown'