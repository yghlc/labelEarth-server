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

def main(options, args):
    pass

if __name__ == '__main__':
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage, version="1.0 2021-10-11")
    parser.description = 'Introduction: export tables from database to excel files'

    parser.add_option("-n", "--max_grids",
                      action="store", dest="max_grids", type=int, default=200,
                      help="the maximum number of grids for process in parallel, large storage allows large number")

    parser.add_option("-w", "--remote_working_dir",
                      action="store", dest="remote_working_dir",
                      help="the working directory in remote machine.")

    parser.add_option("-l", "--remote_log_dir",
                      action="store", dest="remote_log_dir",
                      help="the log directory in remote machine.")

    parser.add_option("-p", "--process_node",
                      action="store", dest="process_node",
                      help="the username and machine for processing ")

    parser.add_option("-d", "--download_node",
                      action="store", dest="download_node",
                      help="the username and machine for download ")

    parser.add_option("", "--b_dont_remove_tmp_folders",
                      action="store_false", dest="b_remove_tmp_folders", default=True,
                      help="if set, then dont remove processing folders of each job")

    parser.add_option("", "--b_dont_remove_DEM_files",
                      action="store_false", dest="b_dont_remove_DEM_files", default=True,
                      help="if set, then dont ArcticDEM (strip and mosaic) that have been processed")

    parser.add_option("", "--b_no_slurm",
                      action="store_true", dest="b_no_slurm", default=False,
                      help="if set, dont submit a slurm job, run job using local machine ")

    parser.add_option("", "--b_main_preProc",
                      action="store_true", dest="b_main_preProc", default=False,
                      help="if set, this computer is the main computer for pre-processing, "
                           "only the main computer would divide a region into subsets, check completeness,"
                           "the main computer must be run")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)
