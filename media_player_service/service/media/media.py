import dbus.service
import subprocess
import threading
from overrides import override
from custom_introspectable import CustomIntrospectable
from event_emitter import Events 
from interface_names import MEDIA_INTERFACE

class Media(CustomIntrospectable):
    def __init__(self, bus, object_path, file_path, interfaces, media_type):
        super().__init__(bus, object_path, interfaces)
        self.file_path = file_path
        self.media_type = media_type
        self.length = 0
        self._playback_process = None
        self.stopped_manually = False

    @override
    def GetDBusProperties(self, interface_name):
        if interface_name == MEDIA_INTERFACE:
            return [
                {'name': 'Type', 'type': 's', 'access': 'read'},
                {'name': 'File', 'type': 's', 'access': 'read'},
                {'name': 'Length', 'type': 'd', 'access': 'read'}
            ]
        return []

    @dbus.service.method(MEDIA_INTERFACE, in_signature='', out_signature='b')
    def Play(self):
        print(f"Playing {self.file_path}")
        try:
            threading.Thread(target=self._play_media).start()

            Events.instance().emit('media_play', self._object_path)

            return True
        except Exception as e:
            print(f"Failed to initiate playback: {e}")
            return False

    def _play_media(self):
        try:
            self._playback_process = subprocess.Popen(['ffplay', '-autoexit', '-nodisp', self.file_path])
            self._playback_process.wait()
            print(f"Finished playing {self.file_path}")

            if self._playback_process.poll() is not None and not self.stopped_manually:
                Events.instance().emit('media_stop', self._object_path)

        except subprocess.CalledProcessError:
            print(f"Error during playback of {self.file_path}")
            Events.instance().emit('media_stop', self._object_path)
        finally:
            self.stopped_manually = False

    @dbus.service.method(MEDIA_INTERFACE, in_signature='', out_signature='b')
    def Stop(self):
        print(f"Stopping media: {self.file_path}")
        try:
            if self._playback_process and self._playback_process.poll() is None:
                self.stopped_manually = True  
                self._playback_process.terminate()
                self._playback_process.wait(timeout=5)
                self._playback_process = None

                Events.instance().emit('media_stop', self._object_path)

                return True
            else:
                print(f"No playback process found or it's already stopped for {self.file_path}")
                return False
        except Exception as e:
            print(f"Failed to stop playback of {self.file_path}: {e}")
            return False
        finally:
            self.stopped_manually = False

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        print(f"Get called for interface: {interface_name}, property: {property_name}")
        if interface_name == MEDIA_INTERFACE:
            if property_name == 'Type':
                return dbus.String(self.media_type)
            elif property_name == 'File':
                return dbus.String(self.file_path)
            elif property_name == 'Length':
                return dbus.Double(self.length)
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.UnknownProperty',
                                                f'No such property {property_name}')