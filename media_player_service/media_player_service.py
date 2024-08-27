from pydbus.generic import signal
from pydbus import SessionBus
from gi.repository import GLib
import os

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

    def Scan(self):
        print("Scanning media directories...")
        self._all_media.clear()

        for directory in self._source_directories:
            if os.path.exists(directory):
                for file_name in os.listdir(directory):
                    if file_name.endswith(('.wav', '.ogg', '.mp3', '.mp4')):
                        media_path = os.path.join(directory, file_name)
                        object_path = self.generate_object_path(media_path)
                        self._all_media.append(object_path)

        self.PropertiesChanged(
            {"AllMedia": self.AllMedia},
            []
        )

        return True

    def AddSource(self, path):
        if os.path.isdir(path):
            self._source_directories.append(path)
            print(f"Source directory {path} added.")

            self.PropertiesChanged(
                {"SourceDirectories": self.SourceDirectories},
                []
            )

            self.Scan()

            return True
        else:
            print(f"Invalid directory: {path}")
            return False

    def generate_object_path(self, media_path):
        
        return "/com/kentkart/RemoteMediaPlayer/Media/" + str(abs(hash(media_path)))


if __name__ == "__main__":
    bus = SessionBus()
    player = RemoteMediaPlayer()

    bus.publish("com.kentkart.RemoteMediaPlayer", player)
    print("Remote Media Player Service is running...")

    loop = GLib.MainLoop()
    loop.run()