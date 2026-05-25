# MCA_PID = {MID} . {[V:F]} . {pkg} . {mod} . {TbF} . { [{ TbN } : {rowN}]...  } . {UUID v7}
from machine_identifier import machine_id, mid_type


def mid():
    if mid_type() == "user_defined":
        print("Give a three letter unqiue nickname: ")
        
