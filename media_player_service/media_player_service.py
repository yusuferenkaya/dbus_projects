from pydbus import SessionBus
from gi.repository import GLib, GObject, Gio
import os
from pydbus.generic import signal
import hashlib



def generate_object_path(media_path):
    # Convert the file path to a valid D-Bus object path
    return '/com/kentkart/RemoteMediaPlayer/Media/' + media_path.replace('/', '_').replace('.', '_')

def is_dbus_object_path(path):
    return GLib.variant_is_object_path(path)


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

class RemoteMediaPlayer:
    """
    <node>
        <interface name='com.kentkart.RemoteMediaPlayer'>
            <property name='Version' type='s' access='read'/>
            <property name='SourceDirectories' type='as' access='read'/>
            <property name='AllMedia' type='ao' access='read'/>
            <method name='Scan'>
                <arg type='b' name='success' direction='out'/>
            </method>
            <method name='AddSource'>
                <arg type='s' name='path' direction='in'/>
                <arg type='b' name='success' direction='out'/>
            </method>
            <signal name='PropertiesChanged'>
                <arg type='s' name='interface_name'/>
                <arg type='a{sv}' name='changed_properties'/>
                <arg type='as' name='invalidated_properties'/>
            </signal>
        </interface>
    </node>
    """

    PropertiesChanged = signal()

    def __init__(self):
        self._version = "1.0"
        self._source_directories = []
        self._all_media = []

    @property
    def Version(self):
        return self._version

    @property
    def SourceDirectories(self):
        return self._source_directories

    @property
    def AllMedia(self):
        return self._all_media

    def AddSource(self, path):
        if os.path.isdir(path):
            self._source_directories.append(path)
            print(f"Source directory {path} added.")

           
            changed_properties = {
                'SourceDirectories': GLib.Variant('as', self._source_directories)
            }

           
            self.PropertiesChanged(
    'com.kentkart.RemoteMediaPlayer',
    GLib.Variant('a{sv}', changed_properties),
    GLib.Variant('as', [])
)
            self.Scan()

            return True
        else:
            print(f"Invalid directory: {path}")
            return False

    def Scan(self):
        print("Scanning media directories...")
        self._all_media.clear()

        for directory in self._source_directories:
            if os.path.exists(directory):
                for file_name in os.listdir(directory):
                    if file_name.endswith(('.wav', '.ogg', '.mp3', '.mp4')):
                        media_path = os.path.join(directory, file_name)
                        object_path = generate_object_path(media_path)
                        self._all_media.append(object_path)

        changed_properties = {}
        if self._all_media:
            # Make sure each item in self._all_media is a valid D-Bus object path
            changed_properties['AllMedia'] = GLib.Variant('ao', self._all_media)

        # Emit the PropertiesChanged signal only if there are changes
        if changed_properties:
            self.PropertiesChanged(
                'com.kentkart.RemoteMediaPlayer',
                GLib.Variant('a{sv}', changed_properties),
                []
            )

        return True



if __name__ == "__main__":
    bus = SessionBus()
    player = RemoteMediaPlayer()

    bus.publish("com.kentkart.RemoteMediaPlayer", player)
    print("Remote Media Player Service is running...")

    loop = GLib.MainLoop()
    loop.run()