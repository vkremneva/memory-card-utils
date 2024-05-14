#!/usr/bin/python3

import argparse
import os
import sqlite3
import math
from zipfile import ZipFile


def split_collection(new_collection_prefix, collection_name, collection_size):
    # get id of the collection we want to split
    collection_id = cur.execute(f"select ID from Collect where Name={collection_name};").fetchone()[0]

    # get id of first collection from the set of splitted collections to create
    start_id = cur.execute("select CollectID from Card order by CollectID desc limit 1;").fetchone()[0] + 1

    # get the amount of new collections
    n_collections = cur.execute(f"select count(distinct ID) from Card where CollectID={collection_id};").fetchone()[0] / float(collection_size)
    n_collections = math.ceil(n_collections)

    # define radix for better naming of new collections
    radix = math.ceil(math.log(n_collections, 10))

    for index, id in zip(
        range(n_collections), 
        range(start_id, start_id + n_collections)
    ):
        new_collection_name = f"{new_collection_prefix} {index:0>{radix}d}"
        cur.execute(f"insert into Collect(Name, IsActive) values ('{new_collection_name}', 0);")
        con.commit()
        cur.execute(f"update Card set CollectID={id} where CollectID = {collection_id} limit {collection_size};")
        con.commit()


parser = argparse.ArgumentParser(description="This script works with save file from app " \
                                 "MemoryCard: splits one collection of words into multiple small collections.")
parser.add_argument("--file", help="Path to the save file you want to work on", 
                    required=True)
parser.add_argument("--cname", help="Name of the collection you want to split",
                    required=True)
parser.add_argument("--nwords", help="Number of words to split by", 
                    required=True)
parser.add_argument("--prefix", help="New prefix name for resulting collections. If no prefix is specified, " \
                    "CNAME is used", default=None)
args = parser.parse_args()

new_collection_prefix = args.prefix if args.prefix is not None else args.cname

# unarchive save file from MemoryCard app which is zip of sqlite datbase
with ZipFile(args.file, 'r') as z:
    z.extractall()

con = sqlite3.connect("memorycard.db")
cur = con.cursor()

split_collection(new_collection_prefix, args.cname, args.nwords)

con.close()  

os.system('zip -m new_save.memorycard memorycard.db images')