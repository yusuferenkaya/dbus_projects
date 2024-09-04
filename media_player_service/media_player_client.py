import dbus
from dbus.mainloop.glib import DBusGMainLoop
import os

def display_menu():
    print("1. Scan Media")
    print("2. Add Source Directory")
    print("3. List All Media")
    print("4. Play Media")
    print("5. View Media Properties")
    print("6. Extract Audio from Video")
    print("7. Reset Media")  
    print("8. List Source Directories")  # New option to list source directories
    print("9. Exit") 

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

        try:
            if choice == '1':
                if player_interface.Scan():
                    print("Media scan initiated.")

            elif choice == '2':
                source = get_user_input("Enter source directory path: ")
                source = os.path.abspath(source)
                if player_interface.AddSource(source):
                    print("Source added successfully.")

            elif choice == '3':
                media_list = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'AllMedia')
                if not media_list:
                    print("No media available.")
                else:
                    for idx, media_path in enumerate(media_list, start=1):
                        print(f"{idx}. {media_path}")

            elif choice == '4':
                media_list = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'AllMedia')
                if not media_list:
                    print("No media available.")
                else:
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
                if not media_list:
                    print("No media available.")
                else:
                    for idx, media_path in enumerate(media_list, start=1):
                        print(f"{idx}. {media_path}")
                    media_choice = int(get_user_input("Select media to view properties: ")) - 1
                    media_path = media_list[media_choice]
                    media_object = bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
                    media_interface = dbus.Interface(media_object, dbus_interface='org.freedesktop.DBus.Properties')
                    
                    media_type = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type')
                    print("Type:", media_type)
                    
                    media_file = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'File')
                    print("File:", media_file)

                    length = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Length')
                    print("Length:", length)
                    
                    if media_type == 'Audio':
                        sample_rate = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'SampleRate')
                        channels = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'Channels')
                        print("Sample Rate:", sample_rate)
                        print("Channels:", channels)
                    
                    elif media_type == 'Video':
                        dimensions = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Video', 'Dimensions')
                        frame_rate = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Video', 'FrameRate')
                        width, height = dimensions[0], dimensions[1]
                        print("Dimensions: ({} x {})".format(width, height))
                        print("Frame Rate:", frame_rate)
                        
                        # Also print audio properties if available
                        try:
                            sample_rate = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'SampleRate')
                            channels = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'Channels')
                            print("Sample Rate:", sample_rate)
                            print("Channels:", channels)
                        except dbus.exceptions.DBusException as e:
                            print("No audio properties available for this video.")

            elif choice == '6':
                media_list = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'AllMedia')
                if not media_list:
                    print("No media available.")
                else:
                    for idx, media_path in enumerate(media_list, start=1):
                        print(f"{idx}. {media_path}")
                    media_choice = int(get_user_input("Select video media to extract audio: ")) - 1
                    media_path = media_list[media_choice]
                    media_object = bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
                    media_interface = dbus.Interface(media_object, dbus_interface='org.freedesktop.DBus.Properties')

                    media_type = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type')
                    if media_type == 'Video':
                        media_video_interface = dbus.Interface(media_object, dbus_interface='com.kentkart.RemoteMediaPlayer.Media.Video')
                        filename = get_user_input("Enter filename for extracted audio: ")
                        if media_video_interface.ExtractAudio(filename):
                            print("Audio extracted successfully.")
                        else:
                            print("Failed to extract audio.")
                    else:
                        print("Selected media is not a video. Cannot extract audio.")
            elif choice == '7': 
                if player_interface.ResetMedia():  
                    print("All media reset successfully.")
                else:
                    print("Failed to reset media.")

            elif choice == '8': 
                source_directories = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'SourceDirectories')
                if not source_directories:
                    print("No source directories available.")
                else:
                    print("Source Directories:")
                    for idx, source_dir in enumerate(source_directories, start=1):
                        print(f"{idx}. {source_dir}")

            elif choice == '9':  
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

        except dbus.DBusException as e:
            print(f"DBus error: {str(e)}")

if __name__ == "__main__":
    main()