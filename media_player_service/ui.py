import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from pydbus import SessionBus
from gi.repository import GLib
import threading
from tkinter import filedialog
from tkinter import messagebox
import dbus
from dbus.mainloop.glib import DBusGMainLoop
bus = SessionBus()
loop = GLib.MainLoop()

class MediaPlayerUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Remote Media Player")
        self.geometry("600x400")
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.create_widgets()
        self.connect_signals()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(6, weight=1)  

    def create_widgets(self):
        self.source_button = ctk.CTkButton(self, text="Add Source Directory", command=self.add_source_directory)
        self.source_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.play_button = ctk.CTkButton(self, text="Play Media", command=self.play_media)
        self.play_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.extract_audio_button = ctk.CTkButton(self, text="Extract Audio from Video", command=self.extract_audio)
        self.extract_audio_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.stop_button = ctk.CTkButton(self, text="Stop Media", command=self.stop_media)
        self.stop_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.view_properties_button = ctk.CTkButton(self, text="View Media Properties", command=self.view_media_properties)
        self.view_properties_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.scan_button = ctk.CTkButton(self, text="Scan Media", command=self.scan_media)
        self.scan_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        self.list_directories_button = ctk.CTkButton(self, text="List Source Directories", command=self.list_source_directories)
        self.list_directories_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.source_directories_listbox = tk.Listbox(self, height=6)
        self.source_directories_listbox.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.playing_media_label = ctk.CTkLabel(self, text="Playing Media", font=("Arial", 14))
        self.playing_media_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.playing_media_tree_view = ttk.Treeview(self, columns=("Media Path",), show="headings", height=5)
        self.playing_media_tree_view.heading("Media Path", text="Media Path")
        self.playing_media_tree_view.grid(row=5, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")

        self.tree_view = ttk.Treeview(self, columns=("Type", "File", "Length"))
        self.tree_view.heading("#0", text="Media Path")
        self.tree_view.heading("Type", text="Type")
        self.tree_view.heading("File", text="File")
        self.tree_view.heading("Length", text="Length")
        self.tree_view.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(6, weight=1) 

        

    def connect_signals(self):
        player_object = self.bus.get_object("com.kentkart.RemoteMediaPlayer", "/com/kentkart/RemoteMediaPlayer")
        player_interface = dbus.Interface(player_object, dbus_interface="com.kentkart.RemoteMediaPlayer")
        properties_interface = dbus.Interface(player_object, dbus_interface="org.freedesktop.DBus.Properties")

        properties_interface.connect_to_signal('PropertiesChanged', self.on_properties_changed)
        player_interface.connect_to_signal('PlayingMediaChanged', self.on_playing_media_changed)

    def on_properties_changed(self, interface_name, changed, invalidated):
        if 'AllMedia' in changed:
            media_list = changed['AllMedia']
            self.update_tree_view(media_list)

    def update_tree_view(self, media_list):
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)

        for media_path in media_list:
            media_object = self.bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
            media_interface = dbus.Interface(media_object, dbus_interface='org.freedesktop.DBus.Properties')

            media_type = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type')
            media_file = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'File')
            media_length = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Length')

            self.tree_view.insert("", "end", text=media_path, values=(media_type, media_file, media_length))

    def on_playing_media_changed(self, playing_media):
        print(f"Currently playing media objects: {playing_media}")

        for item in self.playing_media_tree_view.get_children():
            self.playing_media_tree_view.delete(item)

        if playing_media:
            self.playing_media_label.grid()
            self.playing_media_tree_view.grid()

            for media_path in playing_media:
                self.playing_media_tree_view.insert("", "end", values=(media_path,))
        else:
            self.playing_media_label.grid_remove()
            self.playing_media_tree_view.grid_remove()

    def update_playing_media_list(self, playing_media_list):
        for item in self.tree_view.get_children():
            media_path = self.tree_view.item(item, "text")
            if media_path in playing_media_list:
                self.tree_view.item(item, tags=('playing',))
            else:
                self.tree_view.item(item, tags=(''))
        self.tree_view.tag_configure('playing', background='green')


    def play_media(self):
        selected_item = self.tree_view.focus()
        if selected_item:
            media_path = self.tree_view.item(selected_item, "text")
            media_object = bus.get("com.kentkart.RemoteMediaPlayer", media_path)
            media_interface = media_object["com.kentkart.RemoteMediaPlayer.Media"]
            try:
                if media_interface.Play():
                    print("Media is playing...")
                else:
                    print("Failed to play media.")
            except Exception as e:
                print(f"Error playing media: {e}")
    def view_media_properties(self):
        selected_item = self.tree_view.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a media item to view its properties.")
            return

        media_path = self.tree_view.item(selected_item)["text"]

        try:
            media_object = self.bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
            media_interface = dbus.Interface(media_object, dbus_interface='org.freedesktop.DBus.Properties')

            media_type = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type')
            media_file = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'File')
            media_length = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Length')

            properties_text = f"Type: {media_type}\nFile: {media_file}\nLength: {media_length}"

            if media_type == 'Audio':
                sample_rate = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'SampleRate')
                channels = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Audio', 'Channels')
                properties_text += f"\nSample Rate: {sample_rate}\nChannels: {channels}"

            elif media_type == 'Video':
                dimensions = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Video', 'Dimensions')
                frame_rate = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media.Video', 'FrameRate')
                width, height = dimensions[0], dimensions[1]
                properties_text += f"\nDimensions: {width}x{height}\nFrame Rate: {frame_rate}"

            messagebox.showinfo("Media Properties", properties_text)

        except dbus.DBusException as e:
            messagebox.showerror("Error", f"Failed to retrieve media properties: {e}")


    def stop_media(self):
        selected_item = self.tree_view.focus()
        if selected_item:
            media_path = self.tree_view.item(selected_item, "text")
            media_object = bus.get("com.kentkart.RemoteMediaPlayer", media_path)
            media_interface = media_object["com.kentkart.RemoteMediaPlayer.Media"]
            try:
                if media_interface.Stop():
                    print("Media stopped.")
                else:
                    print("Failed to stop media.")
            except Exception as e:
                print(f"Error stopping media: {e}")

    def add_source_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            player_object = bus.get("com.kentkart.RemoteMediaPlayer", "/com/kentkart/RemoteMediaPlayer")
            player_interface = player_object["com.kentkart.RemoteMediaPlayer"]
            try:
                if player_interface.AddSource(directory):
                    print("Source directory added successfully.")
                else:
                    print("Failed to add source directory.")
            except Exception as e:
                print(f"Error adding source directory: {e}")

    def list_source_directories(self):
        try:
            player_object = self.bus.get_object("com.kentkart.RemoteMediaPlayer", "/com/kentkart/RemoteMediaPlayer")
            properties_interface = dbus.Interface(player_object, dbus_interface="org.freedesktop.DBus.Properties")

            source_directories = properties_interface.Get('com.kentkart.RemoteMediaPlayer', 'SourceDirectories')

            unique_directories = list(set(source_directories))

            self.source_directories_listbox.delete(0, tk.END)
            for directory in unique_directories:
                self.source_directories_listbox.insert(tk.END, directory)

        except dbus.DBusException as e:
            print(f"Error listing source directories: {e}")
            messagebox.showerror("Error", f"Error listing source directories: {e}")

    def extract_audio(self):
        selected_item = self.tree_view.focus()
        if selected_item:
            media_path = self.tree_view.item(selected_item, "text")
            
            GLib.idle_add(self._extract_audio_async, media_path)

    def _extract_audio_async(self, media_path):
        try:
            media_object = self.bus.get_object('com.kentkart.RemoteMediaPlayer', media_path)
            
            media_interface = dbus.Interface(media_object, dbus_interface='org.freedesktop.DBus.Properties')
            
            media_type = media_interface.Get('com.kentkart.RemoteMediaPlayer.Media', 'Type')
            if media_type == 'Video':
                media_video_interface = dbus.Interface(media_object, dbus_interface='com.kentkart.RemoteMediaPlayer.Media.Video')
                if media_video_interface.ExtractAudio():
                    print("Audio extracted successfully.")
                    messagebox.showinfo("Audio Extraction", "Audio extracted successfully.")
                else:
                    print("Failed to extract audio.")
                    messagebox.showerror("Audio Extraction", "Failed to extract audio.")
            else:
                print("Selected media is not a video. Cannot extract audio.")
                messagebox.showwarning("Audio Extraction", "Selected media is not a video. Cannot extract audio.")

        except dbus.DBusException as e:
            print(f"DBus error when extracting audio: {e}")
            messagebox.showerror("Error", f"DBus error when extracting audio: {e}")

        return False 
    def update_media_list(self, media_list):
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)

        for media_path in media_list:
            self.tree_view.insert("", "end", text=media_path, values=("Type", "File", "Length"))

    def scan_media(self):
        try:
            player_object = self.bus.get_object("com.kentkart.RemoteMediaPlayer", "/com/kentkart/RemoteMediaPlayer")
            player_interface = dbus.Interface(player_object, dbus_interface="com.kentkart.RemoteMediaPlayer")
            if player_interface.Scan():
                print("Media scan initiated.")
            else:
                print("Failed to scan media.")
        except dbus.DBusException as e:
            print(f"Error scanning media: {e}")
            messagebox.showerror("Error", f"Error scanning media: {e}")

if __name__ == "__main__":
    threading.Thread(target=loop.run).start()

    app = MediaPlayerUI()
    app.mainloop()