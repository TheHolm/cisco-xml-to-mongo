import xml.etree.ElementTree as ET
import xmltodict

tree = ET.parse('asr04.shl.xml')
root = tree.getroot()
i = 0

element = root.findall("./vrf/definition/")

if not element:  # careful!
    print( "element not found, or element has no subelements" )

if element is None:
    print( "element not found" )


for vrf in element:
   vrf_name = vrf.text
   print ( vrf_name )
   vrf_description = vrf.findall("./description/")
   if vrf_description:
     print( "Description", vrf_description[0].text )



#for interface in root.find('interface'):
#  print( interface.tag, interface.attrib)
#  i = i + 1
#  print( i )