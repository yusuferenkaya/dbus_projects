from pydbus import SessionBus
from gi.repository import GLib

count = 0

def PropertiesChanged(iface, values, invalidated):
    print('------------------------------------------------------------')
    print(f'Interface: {iface}')
    print(f'Values: {values}')
    print(f'Invalidated: {invalidated}')
    print('------------------------------------------------------------')
    print()

def AddSourceCb(s):
    global count
    count += 1
    s.AddSource(f'/home/osboxes/dir{count}')

    return True


if __name__ == '__main__':
    loop = GLib.MainLoop()
    
    bus = SessionBus()
    s = bus.get('com.kentkart.RemoteMediaPlayer')
    s.onPropertiesChanged = PropertiesChanged
    
    GLib.timeout_add_seconds(1, AddSourceCb, s)
    
    loop.run()