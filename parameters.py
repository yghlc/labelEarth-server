#!/usr/bin/env python
# Filename: parameters.py
"""
introduction: get the parameter from file

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 06 May, 2016
"""

import sys,os

saved_parafile_path ='para_default.ini'

def read_Parameters_file(parafile,parameter):
    try:
      inputfile = open(parafile, 'r')
    except IOError:
      raise IOError("Error: Open file failed, path: %s"%os.path.abspath(parafile))
    list_of_all_the_lines = inputfile.readlines()
    value = False
    for i in range(0,len(list_of_all_the_lines)):
        line = list_of_all_the_lines[i]
        if line[0:1] == '#' or len(line) < 2:
            continue
        lineStrs = line.split('=')
        lineStrleft = lineStrs[0].strip()     #remove ' ' from left and right
        if lineStrleft.upper() == parameter.upper():
            value = lineStrs[1].strip()
            break
    inputfile.close()
    return value

def get_string_parameters(parafile,name):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False:
        raise ValueError('get %s parameter failed'%name)
    else:
        return result

def get_string_parameters_None_if_absence(parafile,name):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False or len(result) < 1:
        return None
    else:
        return result

def get_bool_parameters_None_if_absence(parafile,name):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False or len(result) < 1:
        return None
    if result.upper()=='YES':
        return True
    else:
        return False

def get_bool_parameters(parafile,name):
    value = get_bool_parameters_None_if_absence(parafile,name)
    if value is None:
        raise ValueError(' %s not set in %s' % (name, parafile))
    return value

def get_digit_parameters_None_if_absence(parafile,name,datatype):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False or len(result) < 1:
        return None
    try:
        if datatype == 'int':
            digit_value = int(result)
        else:
            digit_value = float(result)
    except ValueError:
            raise ValueError('convert %s to digit failed , exit'%(name))

    return digit_value

def get_digit_parameters(parafile,name,datatype):
    value = get_digit_parameters_None_if_absence(parafile, name, datatype)
    if value is None:
        raise ValueError(' %s not set in %s'%(name, parafile))
    return value


def test_readparamters():
    parafile = 'setting.ini'

    return True

def main():
    test_readparamters()
    pass


if __name__=='__main__':
    main()
