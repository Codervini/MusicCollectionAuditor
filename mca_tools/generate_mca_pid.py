# MCA_PID = {MID} . {[V:F]} . {pkg} . {mod} . {TbF} . { [{ TbN } : {rowN}]...  } . {UUID v7}
from machine_identifier import machine_id, mid_type, smid
import enum
from mca.core.db_butler import count_table_rows
import math
import base64

b64URLChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

def encodeb64URL_in_2char(n):
    if n >= 64 * 64:
        raise ValueError("Too large for 2 chars")
    return b64URLChar[n // 64] + b64URLChar[n % 64]

def set_number(table):
    setn =  math.floor(count_table_rows(table) / 16777215)
    setnb64 = encodeb64URL_in_2char(setn)
    print(setn,setnb64)
    return [setn,setnb64]

def row_number(table):
    rownum = count_table_rows(table) // (set_number(table)[0] + 1)
    print(rownum)


set_number("artists")
row_number("artists")