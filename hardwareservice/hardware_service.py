from pydbus import SessionBus
from gi.repository import GLib
import psutil
import platform
import shutil

class HardwareService:
    """
    <node>
        <interface name='hardware.service'>
            <method name='GetCPUInfo'>
                <arg type='s' name='info' direction='out'/>
            </method>
            <method name='GetMemoryInfo'>
                <arg type='s' name='info' direction='out'/>
            </method>
            <method name='GetDiskInfo'>
                <arg type='s' name='info' direction='out'/>
            </method>
            <method name='GetNetworkInfo'>
                <arg type='s' name='info' direction='out'/>
            </method>
            <method name='GetSystemInfo'>
                <arg type='s' name='info' direction='out'/>
            </method>
        </interface>
    </node>
    """
    
    def GetCPUInfo(self):
        cpu_info = f"CPU: {platform.processor()}\nCores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical\nUsage: {psutil.cpu_percent(interval=1)}%"
        return cpu_info

    def GetMemoryInfo(self):
        mem = psutil.virtual_memory()
        memory_info = f"Total: {mem.total // (1024 ** 2)} MB\nAvailable: {mem.available // (1024 ** 2)} MB\nUsed: {mem.used // (1024 ** 2)} MB\nPercentage: {mem.percent}%"
        return memory_info

    def GetDiskInfo(self):
        disk_usage = shutil.disk_usage("/")
        disk_info = f"Total: {disk_usage.total // (1024 ** 3)} GB\nUsed: {disk_usage.used // (1024 ** 3)} GB\nFree: {disk_usage.free // (1024 ** 3)} GB\nPercentage: {100 * disk_usage.used / disk_usage.total:.2f}%"
        return disk_info

    def GetNetworkInfo(self):
        net_info = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == 2:  # AF_INET (IPv4)
                    net_info.append(f"Interface: {interface}\nIP Address: {addr.address}")
        return "\n".join(net_info) if net_info else "No network interfaces found."

    def GetSystemInfo(self):
        system_info = f"System: {platform.system()}\nNode Name: {platform.node()}\nRelease: {platform.release()}\nVersion: {platform.version()}\nMachine: {platform.machine()}\nProcessor: {platform.processor()}"
        return system_info

if __name__ == "__main__":
    bus = SessionBus()
    bus.publish("hardware.service", HardwareService())

    print("Hardware service is running...")

    loop = GLib.MainLoop()
    loop.run()