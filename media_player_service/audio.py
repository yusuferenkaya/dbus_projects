# audio.py

from media import Media

class Audio(Media):
    """
    <node>
        <interface name='com.kentkart.RemoteMediaPlayer.Media.Audio'>
            <property name='SampleRate' type='i' access='read'/>
            <property name='Length' type='d' access='read'/>
            <property name='Channels' type='i' access='read'/>
        </interface>
    </node>
    """

    def __init__(self, file_path, sample_rate, length, channels):
        super().__init__(file_path)
        self._type = 'Audio'
        self._sample_rate = sample_rate
        self._length = length
        self._channels = channels

    @property
    def SampleRate(self):
        return self._sample_rate

    @property
    def Length(self):
        return self._length

    @property
    def Channels(self):
        return self._channels