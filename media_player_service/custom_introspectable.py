import dbus.service
import xml.etree.ElementTree as ET

class CustomIntrospectable(dbus.service.Object):
    def __init__(self, bus, object_path):
        super().__init__(bus, object_path)
        self.interface_name = None  

    @dbus.service.method(dbus.INTROSPECTABLE_IFACE, in_signature='', out_signature='s',
                         path_keyword='object_path', connection_keyword='connection')
    def Introspect(self, object_path, connection):
        xml = super().Introspect(object_path, connection)
        try:
            root = ET.ElementTree(ET.fromstring(xml)).getroot()
            iface_node = root.find(f".//interface[@name='{self.interface_name}']")
            
            if iface_node is None:
                return xml
            
            for prop in self.GetDBusProperties():
                prop_element = ET.Element('property', {
                    'name': prop['name'],
                    'type': prop['type'],
                    'access': prop['access']
                })
                iface_node.append(prop_element)

            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            print(f"Error in Introspect method: {e}")
            return xml

    def GetDBusProperties(self):
        
        return []