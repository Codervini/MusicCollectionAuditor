import pymongo
from mca_tools.mca_pid_enums import TableName
from mca_tools.generate_mca_pid import _total_row_number
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mdb = mongo_client["mca_table_stats"]
mtb = mdb["mca_tables_highest_row_count"]

def init_record_row_count():
    data = {}
    for i in TableName:
        data[i.value] = _total_row_number(i.value)[0]
    print(data)

    result = mtb.insert_one(data)

    # print("Inserted:", result.inserted_id)
    # print("Databases:", mongo_client.list_database_names())
    # print("Collections:", mdb.list_collection_names())

def update_table_row_count(table):
    

# record_row_count()