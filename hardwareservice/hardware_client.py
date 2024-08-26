import dbus

def show_menu():
    print("\n--- Hardware Information Client ---")
    print("1. Get CPU Info")
    print("2. Get Memory Info")
    print("3. Get Disk Info")
    print("4. Get Network Info")
    print("5. Get System Info")
    print("6. Exit")
    choice = input("Enter your choice: ")
    return choice

if __name__ == "__main__":
    bus = dbus.SessionBus()
    hardware_object = bus.get_object('hardware.service', '/hardware/service')
    hardware_interface = dbus.Interface(hardware_object, dbus_interface='hardware.service')

    while True:
        choice = show_menu()

        try:
            if choice == '1':
                cpu_info = hardware_interface.GetCPUInfo()
                print("\nCPU Information:")
                print(cpu_info)
            elif choice == '2':
                memory_info = hardware_interface.GetMemoryInfo()
                print("\nMemory Information:")
                print(memory_info)
            elif choice == '3':
                disk_info = hardware_interface.GetDiskInfo()
                print("\nDisk Information:")
                print(disk_info)
            elif choice == '4':
                network_info = hardware_interface.GetNetworkInfo()
                print("\nNetwork Information:")
                print(network_info)
            elif choice == '5':
                system_info = hardware_interface.GetSystemInfo()
                print("\nSystem Information:")
                print(system_info)
            elif choice == '6':
                print("Exiting...")
                break
            else:
                print("Invalid choice, please try again.")
        except dbus.DBusException as e:
            print(f"DBus error: {str(e)}")