import json
from pathlib import Path
from pprint import pprint
import machineid
import socket
import platform
import datetime

def generate_new_machine_id(path, machine_id_json:dict,id_type:str="system_defined"):
    '''type = user_defined or system_defined'''

    if id_type == "system_defined":
        id_config = {
                "name": socket.gethostname(),
                "type": "system_defined",
                "current_uuid": machineid.id(),
                "previous_uuids": [],
                "os": platform.system(),
                "first_seen": str(datetime.datetime.now()),
                "last_seen": ""
            }
        machine_id_json["saved_machines"][machineid.id()] = id_config
    elif id_type == "user_defined":
        name = str(input("Name of Machine ID: "))

        if machine_id_json["saved_machines"].get(name,None):
            print("ID with same name already present")
            choice = int(input('''1) To add current system GUID under same name
                                  2) To skip 
                                    Choice: '''))    
            match choice:
                case 1:
                    machine_id_json["saved_machines"][name]["previous_uuids"].append(machineid.id())
                case 2:
                     machine_id_json["saved_machines"][name]["previous_uuids"] = []
                case _:
                    print("Invalid option")
            
        id_config = {
                "name": name,
                "type": "user_defined",
                "current_uuid": machineid.id(),
                "os": platform.system(),
                "first_seen": str(datetime.datetime.now()),
                "last_seen": ""
            }
        machine_id_json["saved_machines"][name] = id_config

    with open(path,"w") as f:
        json.dump(machine_id_json,f)

    


def machine_id():
    config = Path("data","config.json")

    with open(config,"r") as f:
        machine_id_json = json.load(f)["machine_id"]
    # pprint(machine_id_json)


    if machine_id_json["current_id"]:
        if machine_id_json["saved_machines"].get(machine_id_json["current_id"],None):
            print(f"Valid Current Machine id: {machine_id_json["current_id"]}")
            return machine_id_json["current_id"]
        else:
            print("Invalid Current Machine id, please select valid ID or make new")
    elif not machine_id_json["current_id"]:
        if machine_id_json["saved_machines"]:
            print(f"Machine ID not selected, please select a ID or make new")
        else:
            print("No ID available, make new")
            generate_new_machine_id(config,machine_id_json,"user_defined")
            return machine_id
    return None
# json.dump()

print(machine_id())
