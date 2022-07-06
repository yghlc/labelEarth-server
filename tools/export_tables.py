#!/usr/bin/env python
# Filename: export_tables.py 
"""
introduction:

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 06 July, 2022
"""

import os, sys
from optparse import OptionParser
import pandas as pd
import json

from datetime import datetime

all_table_names = ['auth.user', 'imageObjects.image','imageObjects.userinput']

def convert_json_to_excel(json_path, xlsx_path):
    with open(json_path) as f_obj:
        json_list = json.load(f_obj)
    
    print('\n record Count:', len(json_list))
    # print(json_list[0])
    records = {}
    for rec in json_list:
        if 'pk' in records.keys():
            records['pk'].append(rec['pk'])
        else:
            records['pk'] = [rec['pk']]

        
        fields = rec['fields']
        for key in fields.keys():
            if key in records.keys():
                records[key].append(fields[key])
            else:
                records[key] = [fields[key]]

     # save to excel file
    table_pd = pd.DataFrame(records)
    with pd.ExcelWriter(xlsx_path) as writer:
        table_pd.to_excel(writer) # sheet_name='training parameter and results'
        # # set format
        # workbook = writer.book
        # format = workbook.add_format({'num_format': '#0.000'})
        # train_out_table_sheet = writer.sheets['training parameter and results']
        # train_out_table_sheet.set_column('O:P',None,format)



def export_a_table(table_name, save_dir, save_table_name=None):
    save_table_pre_name = save_table_name if save_table_name is not None else table_name.replace('.','-')
    save_json = os.path.join(save_dir, '%s.json'%save_table_pre_name)
    command_str = 'python manage.py dumpdata %s --indent 2 > %s'%(table_name,save_json)
    res = os.system(command_str)
    if res != 0:
        sys.exit(res)
    
    save_xlsx = os.path.join(save_dir,'%s.xlsx'%save_table_pre_name)
    # convert json to excel table
    convert_json_to_excel(save_json,save_xlsx)
    
def test_convert_json_to_excel():
    print(datetime.now(),'testing convert json excel')
    save_json = 'imageObjects-image.json'
    save_xlsx = 'output.xlsx'
    convert_json_to_excel(save_json,save_xlsx)

def main(options, args):
    # test_convert_json_to_excel()
    # sys.exit(1)
    
    # table_name = options.table_name 
    table_name = args[0]
    save_dir = options.save_dir if options.save_dir is not None else './'
    export_tables = [ table_name ] if table_name is not None else all_table_names
    for table in export_tables:
        print(datetime.now(),'exporting %s'%table)
        export_a_table(table, save_dir)


    pass

if __name__ == '__main__':
    usage = "usage: %prog [options] table-name"
    parser = OptionParser(usage=usage, version="1.0 2021-10-11")
    parser.description = 'Introduction: export tables from database to excel files, table_names: imageObjects.image, auth.user, and imageObjects.userinput'

    # parser.add_option("-n", "--table_name",
    #                   action="store", dest="table_name", default='imageObjects.image',
    #                   help="the name of tables want to export, others: auth.user and imageObjects.userinput")

    parser.add_option("-d", "--save_dir",
                      action="store", dest="save_dir",
                      help="the directory to save the exported tables")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)
