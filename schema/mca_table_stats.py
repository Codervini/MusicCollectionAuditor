import pymongo
from mca_tools.mca_pid_enums import TableName
from mca_tools.pid_utilities import _total_row_number_normalised_by_setnumber
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mdb = mongo_client["mca_table_stats"]
mtb = mdb["mca_tables_highest_row_count"]

def init_record_row_count():
    data = {}
    for i in TableName:
        data[i.value] = _total_row_number_normalised_by_setnumber(i.value)[0]
    print(data)

    result = mtb.update_one({"_id":"hrc"},{"$set":data},upsert=True)

def update_table_row_count(table):
    mtb.update_one({"_id":"hrc"},{"$set":{table:_total_row_number_normalised_by_setnumber(table)[0]}})

def show_table_row_count(table):
    doc = mtb.find_one({"_id": "hrc"})
    print(doc["meta_processor_runs"])

init_record_row_count()
show_table_row_count("meta_processor_runs")
update_table_row_count("meta_processor_runs")