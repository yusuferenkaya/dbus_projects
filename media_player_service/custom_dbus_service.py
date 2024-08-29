import dbus
import dbus.service

import xml.etree.ElementTree as ET

from typing import List

class DBusProperty:

    def __init__(self, name, type, access) -> None:
        self.name = name
        self.type = type
        self.access = access


class CustomDBusService(dbus.service.Object):

    def __init__(self, bus, object_path, interface_name):
        super().__init__(bus, object_path)
        self.bus = bus
        self.interface_name = interface_name

    def GetDBusProperties(self) -> List[DBusProperty]:
        """A function that returns List of DBusProperty objects"""
        raise NotImplementedError('Child classes must implement this function')


    @dbus.service.method(dbus.INTROSPECTABLE_IFACE, in_signature='', out_signature='s',
                         path_keyword='object_path', connection_keyword='connection')
    def Introspect(self, object_path, connection):
        xml = super().Introspect(object_path, connection)
        try:
            root = ET.ElementTree(ET.fromstring(xml)).getroot()
            iface_node = root.find(f".//interface[@name='{self.interface_name}']")
            if not iface_node:
                return xml
            
            for prop in self.GetDBusProperties():
                iface_node.append(ET.Element('property', {
                    'type': prop.type,
                    'access': prop.access,
                    'name': prop.name 
                }))
            
            return ET.tostring(root)
        except Exception as e:
            print(f'Error: {e}')
            return xml