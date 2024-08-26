import dbus
from dbus.mainloop.glib import DBusGMainLoop
import sys
import os
def display_menu():
    print("1. Scan Media")
    print("2. Add Source Directory")
    print("3. List All Media")
    print("4. Play Media")
    print("5. View Media Properties")
    print("6. Extract Audio from Video")
    print("7. Exit")

def get_user_input(prompt):
    return input(prompt).strip()

def on_properties_changed(interface_name, changed, invalidated):
    print(f"Properties changed on interface {interface_name}: {changed}")
    if 'AllMedia' in changed:
        print("Updated AllMedia: ", changed['AllMedia'])
    if 'SourceDirectories' in changed:
        print("Updated SourceDirectories: ", changed['SourceDirectories'])



def main():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    
    player_object = bus.get_object('com.kentkart.RemoteMediaPlayer', '/com/kentkart/RemoteMediaPlayer')
    player_interface = dbus.Interface(player_object, dbus_interface='com.kentkart.RemoteMediaPlayer')
    properties_interface = dbus.Interface(player_object, dbus_interface='org.freedesktop.DBus.Properties')

    properties_interface.connect_to_signal('PropertiesChanged', on_properties_changed)

    while True:
        display_menu()
        choice = get_user_input("Choose an option: ")

        if choice == '1':
            try:
                player_interface.Scan()
                print("Media scan initiated.")
            except dbus.DBusException as e:
                print(f"DBus error during Scan: {str(e)}")
        elif choice == '2':
            source = get_user_input("Enter source directory path: ")
            
            source = os.path.abspath(source)
            
            try:
                if player_interface.AddSource(source):
                    print("Source added successfully.")
                else:
                    print("Invalid directory.")
            except dbus.DBusException as e:
                print(f"DBus error during AddSource: {str(e)}")
        elif choice == '3':
            media_list = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'AllMedia')
            for idx, media_path in enumerate(media_list, start=1):
                print(f"{idx}. {media_path}")
        elif choice == '4':
            media_list = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'AllMedia')
            for idx, media_path in enumerate(media_list, start=1):
                print(f"{idx}. {media_path}")
            media_choice = int(get_user_input("Select media to play: ")) - 1
            media_path = media_list[media_choice]
            media_object = bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
            media_interface = dbus.Interface(media_object, dbus_interface='com.kentkart.RemoteMediaPlayer.Media')
            if media_interface.Play():
                print("Media is playing...")
            else:
                print("Failed to play media.")
        elif choice == '5':
            media_list = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'AllMedia')
            for idx, media_path in enumerate(media_list, start=1):
                print(f"{idx}. {media_path}")
            media_choice = int(get_user_input("Select media to view properties: ")) - 1
            media_path = media_list[media_choice]
            media_object = bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
            media_interface = dbus.Interface(media_object, dbus_interface='org.freedesktop.DBus.Properties')
            
            print("Type:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type'))
            print("File:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'File'))
            
            if media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type') in ['WAV', 'OGG', 'MP3']:
                print("Sample Rate:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'SampleRate'))
                print("Length:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'Length'))
                print("Channels:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'Channels'))
            
            if media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type') == 'MP4':
                print("Length:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Video', 'Length'))
                print("Dimensions:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Video', 'Dimensions'))
                print("Frame Rate:", media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Video', 'FrameRate'))
        elif choice == '6':
            media_list = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'AllMedia')
            for idx, media_path in enumerate(media_list, start=1):
                print(f"{idx}. {media_path}")
            media_choice = int(get_user_input("Select video media to extract audio: ")) - 1
            media_path = media_list[media_choice]
            media_object = bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
            media_interface = dbus.Interface(media_object, dbus_interface='com.kentkart.RemoteMediaPlayer.Media.Video')
            filename = get_user_input("Enter filename for extracted audio: ")
            if media_interface.ExtractAudio(filename):
                print("Audio extracted successfully.")
            else:
                print("Failed to extract audio.")
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()