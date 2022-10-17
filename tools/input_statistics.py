#!/usr/bin/env python
# Filename: input_statistics.py 
"""
introduction: statistics on the input of each user, the progress of image validation

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 17 September, 2022
"""

import os, sys
import pandas as pd

from datetime import datetime

# run export_tables.py to get xlsx files
xlsx_tables = ['auth-user.xlsx','imageObjects-image.xlsx','imageObjects-userinput.xlsx']
max_valid_times = 3     # each image should only be validated less than 3 times.

def statistics_input_from_each_user(user_table, input_table):
    # statistics on the input of each user
    input_user_ids = input_table['user_name'].to_list()
    unique_user_ids  = set(input_user_ids)
    user_input = {}
    for user_id in unique_user_ids:
        loc = user_table['pk'] == user_id
        user_name = user_table[ loc ]['username'].to_list()[0]
        user_email = user_table[loc ]['email'].to_list()[0]
        input_count = input_user_ids.count(user_id)
        # print(user_name, user_email,input_count)
        # break
        user_input.setdefault('user_name', []).append(user_name)
        user_input.setdefault('user_email', []).append(user_email)
        user_input.setdefault('input_count', []).append(input_count)

    # print(user_input)
    # save to excel file
    save_path = 'user_input_statistics_%s.xlsx'% datetime.now().strftime('%Y%m%d-%H%M%S')
    table_pd = pd.DataFrame(user_input)
    with pd.ExcelWriter(save_path) as writer:
        table_pd.to_excel(writer) # sheet_name='training parameter and results'
    print('save to %s'%os.path.abspath(save_path))

def statistics_validate_progress(image_table,input_table):
    image_valid_times_list = image_table['image_valid_times'].to_list()
    image_count = len(image_valid_times_list)

    valid_time_img_count = {}
    check_image_count = 0
    total_input_count = 0
    for k in range(max_valid_times+1):
        # print(k)
        count = image_valid_times_list.count(k)
        valid_time_img_count[k] = count
        check_image_count += count
        total_input_count += count*k
    unexpected_count = image_count - check_image_count  # the number of images be validated for more than "max_valid_times(=3)"

    # statistics from the input table
    image_id_list = input_table['image_name']
    user_note_list = input_table['user_note']
    rm_count = 0
    new_image_id_list = []
    for img_id, user_note in zip(image_id_list,user_note_list):
        if user_note == 'copy from lingcao.huang@colorado.edu':
            rm_count += 1
            continue
        new_image_id_list.append(img_id)
    unique_ids = set(new_image_id_list)
    id_repeat_times = [new_image_id_list.count(item) for item in unique_ids]

    save_path = 'validate_progress_statistics_%s.txt' % datetime.now().strftime('%Y%m%d-%H%M%S')
    with open(save_path,'w') as f_obj:
        f_obj.writelines('total image count: %d, each need to be validated %d time, have got %d input from users, progress: %.4f percent \n'%
                         (image_count, max_valid_times, total_input_count, total_input_count*100.0/(image_count*max_valid_times)) )

        for k in range(max_valid_times + 1):
            f_obj.writelines('%d images have been validated %d times\n'%(valid_time_img_count[k],k))

        f_obj.writelines('%d images have been validated more than %d times\n' % (unexpected_count, max_valid_times))

        # base on the statistics of input table
        f_obj.writelines('\n\n\nbased on Input table after filtering (remove %d ones), have got %d input from users, progress: %.4f percent \n' %
            (rm_count, sum(id_repeat_times), sum(id_repeat_times) * 100.0 / (image_count * max_valid_times)))
        for k in sorted(set(id_repeat_times)):
            f_obj.writelines('%d images have been validated %d times\n' % (id_repeat_times.count(k), k))

    print('save to %s' % os.path.abspath(save_path))


def main():
    # check file existence
    for ff in xlsx_tables:
        if os.path.isfile(ff) is False:
            raise IOError('%s does not exist in the directory: %s'%(ff,os.getcwd()))

    # read tables
    user_table = pd.read_excel(xlsx_tables[0])
    image_table = pd.read_excel(xlsx_tables[1])
    input_table = pd.read_excel(xlsx_tables[2])

    # statistics and save results
    statistics_input_from_each_user(user_table,input_table)
    statistics_validate_progress(image_table,input_table)

if __name__ == '__main__':
    main()