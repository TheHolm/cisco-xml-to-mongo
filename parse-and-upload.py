import xmltodict
import pprint
import json
import configparser
import sys
import argparse
from pymongo import MongoClient

def parse_command_line():
  # hha [-c config file ] cisco_config.xml 
  # --config -c config file name - default is parse.conf
   parser = argparse.ArgumentParser(description='Parce Cisco config in XML form and upload it to MongoDB.')
   parser.add_argument('-c', '--config', type=argparse.FileType('r'), nargs='?',default='parse.conf', help='%(prog)s configuration file')
   parser.add_argument(metavar='configuration_file.xml', dest='input_file', type=argparse.FileType('r'), help='Cisco router config in XML format "sh run | format xml"')
   parser.add_argument('-v','--version', action='version', version='%(prog)s 0.01')
   args = parser.parse_args()
   return args

#end of parse_command_line()

def load_configuration_file(config_file_handler):

   config_defaults = {'database_host': '127.0.0.1',
                                   'database_port': 27017,
                                   'database_user': '',
                                   'database_password': '',
                                   'database_name': 'config-database'
                     }

   config = configparser.ConfigParser(config_defaults)
   try:
     config.read_file(config_file_handler)
   except Error:
    print("Unexpected error:", sys.exc_info()[0])
    quit(1)

# end of load_configuration_file()

def config_iterator(config_dict, database_export_dict, depth):
    # yes, I know how wastefull such recursion is
    # print("Down Depth: ", depth)
    depth = depth + 1
    if type(config_dict) == list:    ### !!!! OH it is a list, need to dive to each element of it
        for item in config_dict:
            config_iterator(item, database_export_dict, depth)    # RECURSION !!!!

    else:    # it is no a list, keep diving.
        for config_item in database_export_dict:
            if config_item in config_dict:    # does this branch present in config? 
                # print("Desending down to: ", config_item, " Type: ", type(database_export_dict[config_item]))
                if type(database_export_dict[config_item]) == str:    # end of the way. Leaf. 
                    # print("Leaf reached: ", config_item, "Depth: ", depth)
                    for item in config_dict:
                        if item == config_item:
                          if type(config_dict[item]) == list : # need to iterate over all elements.
                              collection = db[database_export_dict[config_item]]
                              for list_item in config_dict[item]:
                               #   print(database_export_dict[config_item], " ---- ", json.dumps(list_item))
                                  collection.insert_one(list_item)
                          else:
                              collection = db[database_export_dict[config_item]]
                            #  print(database_export_dict[config_item], " ---- ", json.dumps(config_dict[config_item]))
                              collection.insert_one(config_dict[config_item])
                          
                else:
                    # we are not yet in leaf
                    for item in database_export_dict:
                        if item == config_item:
                           # print("Item: ", item, "Dept: ", depth)
                            config_iterator(config_dict[config_item], database_export_dict[item], depth)    # RECURSION !!!!
    depth = depth - 1
    # print("Up Depth: ", depth)

# end of config_iterator

#### --- Main() --- ####

pp = pprint.PrettyPrinter(indent=1)

args = parse_command_line()

load_configuration_file(vars(args)['config'])


file_h = vars(args)['input_file']
config_dict = xmltodict.parse(file_h.read())['Device-Configuration']

database_client = MongoClient()
database_client.drop_database('test-database')
db = database_client['test-database']


database_export_dict = {
                         'hostname' : 'hostname',
                         'vrf': {'definition': 'vrf_list'}, 
                         'ip': {'vrf': 'vrf_list', 'prefix-list': 'prefix_list'},
                         'interface' : 'interfaces',
                         'route-map': 'route_map',
			 'access-list' : 'access_lists'
}



config_iterator(config_dict, database_export_dict, 0)

file_h.close()
quit()
"""
odict_keys(['version', 
'service', 
'platform', 
'hostname', 
'boot-start-marker',
'boot', 
'boot-end-marker', 
'aqm-register-fnf', 
'vrf', 
'logging', 
'enable', 
'aaa', 
'process', 
'clock', 
'ip',  - -there are VRF there too. 
'login', 
'ipv6', 
'subscriber', 
'mpls', 
'clns', 
'multilink', 
'l2vpn', 
'key', 
'X-Interface', 
'spanning-tree', 
'username', 
'redundancy', 
'class-map', 
'policy-map', 
'class', 
'description', 
'interface', 
'router', 
'access-list', 
'route-map', 
'snmp-server', 
'snmp', 
'tacacs-server', 
'tacacs', 
'control-plane', 
'banner', 
'line', 
'ntp', 
'end'])
"""
