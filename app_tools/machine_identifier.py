import json
from pathlib import Path
from pprint import pprint
import machineid
import socket
import platform
import datetime

def generate_new_machine_id(path:Path, full_json:dict, id_type:str="system_defined"):
    '''type = user_defined or system_defined, generates new machine id data and returns newly generated id'''
    machine_id_json = full_json["machine_id"]
    machine_id = machineid.id()

    if id_type == "system_defined":
        id_config = {
                "name": socket.gethostname(),
                "type": "system_defined",
                "current_uuid": machine_id,
                "previous_uuids": [],
                "os": platform.system(),
                "first_seen": str(datetime.datetime.now()),
                "last_seen": ""
            }
        machine_id_json["saved_machines"][machine_id] = id_config
    elif id_type == "user_defined":
        machine_id = str(input("Name of Machine ID: "))

        if machine_id_json["saved_machines"].get(machine_id,None):
            print("ID with same name already present")
            choice = int(input('''1) To add current system GUID under same name
                                  2) To skip 
                                    Choice: '''))    
            match choice:
                case 1:
                    machine_id_json["saved_machines"][machine_id]["previous_uuids"].append(machineid.id())
                case 2:
                    #  machine_id_json["saved_machines"][machine_id]["previous_uuids"] = []
                    pass
                case _:
                    print("Invalid option")
            
        id_config = {
                "name": machine_id,
                "type": "user_defined",
                "current_uuid": machineid.id(),
                "previous_uuids": [],
                "os": platform.system(),
                "first_seen": str(datetime.datetime.now()),
                "last_seen": ""
            }
        machine_id_json["saved_machines"][machine_id] = id_config

    full_json["machine_id"] = machine_id_json

    with open(path,"w") as f:
        json.dump(full_json,f)

    return machine_id

def set_current_machine_id(path:Path,full_json:dict):
    '''Sets a current_machine_id and returns it'''
    machine_id_json = full_json["machine_id"]
    counter = 0
    key_list = []
    print()

    for k, v in machine_id_json["saved_machines"].items():
        print(f"{counter+1}) ID: {k} | OS:{v["os"]} | Last Used: {v["last_seen"]}")
        key_list.append(k)
        counter += 1
    choice = int(input("Which ID to set as current user ID? Enter number to select: ").strip())
    if choice > len(key_list) or choice < 1:
        print("Invalid Option selected!")
        return None
    choosen_id = key_list[choice-1]

    if machine_id_json["saved_machines"][choosen_id]["os"] != platform.system():
        print("Selected ID was meant for another OS, choose only same OS ID")
        return None
        # return set_current_machine_id(path,full_json)

    machine_id_json["current_id"] = choosen_id

    full_json["machine_id"] = machine_id_json
    with open(path,"w") as f:
        json.dump(full_json,f)

    return machine_id_json["current_id"]

    


def machine_id():
    '''Handles machine_id logic. Returns machine_id or else None if theres an error'''
    config = Path("data","config.json")

    with open(config,"r") as f:
        full_json = json.load(f)
        machine_id_json = full_json["machine_id"]
    # pprint(machine_id_json)


    if machine_id_json["current_id"]:
        if machine_id_json["saved_machines"].get(machine_id_json["current_id"],None):
            if machine_id_json["saved_machines"][machine_id_json["current_id"]]["os"] == platform.system():
                print(f"Valid Current Machine id: {machine_id_json["current_id"]}")
                return machine_id_json["current_id"]
            else:
                print("Selected ID was meant for another OS, choose only same OS ID")
                return set_current_machine_id(config,full_json)

        else:
            print("Invalid Current Machine id, please select valid ID or make new")
            return set_current_machine_id(config,full_json)
    elif not machine_id_json["current_id"]:
        if machine_id_json["saved_machines"]:
            print(f"Machine ID not selected, please select a ID or make new")
            return set_current_machine_id(config,full_json)
        else:
            print("No ID available, make new")
            generate_new_machine_id(config,full_json,"user_defined")
            return machine_id()
    return None
# json.dump()
# machine_id()
# print(machine_id())
