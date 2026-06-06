import math
from mca.core.db_butler import count_table_rows
b64URLChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def number_to_encodeb64URL_in_2char(n):
    if n >= 64 * 64:
        raise ValueError("Too large for 2 chars")
    return b64URLChar[n // 64] + b64URLChar[n % 64]

def number_to_encodeb64URL_in_4char(n):
    reversed_b64URL = []
    if n >= 64 ** 4:
        raise ValueError("Too large for 4 chars")
    for _ in range(0,4):
        reversed_b64URL.append(b64URLChar[int(n % 64)])
        n /= 64
    reversed_b64URL.reverse()
    return "".join(reversed_b64URL)

def set_number(table):
    # from mca.core.db_butler import count_table_rows
    setn =  math.floor(count_table_rows(table) / 16777215)
    setnb64 = number_to_encodeb64URL_in_2char(setn)
    return [setn,setnb64]

def _total_row_number_normalised_by_setnumber(table):

    rownum = count_table_rows(table) // (set_number(table)[0] + 1)
    rownumb64 = number_to_encodeb64URL_in_4char(rownum)
    return [rownum,rownumb64]
