from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse

from imageObjects.models import Image
from tools.common import get_one_record
from tools.common import get_available_image

from datetime import datetime
import json

# Create your views here.
def index(request):
    return HttpResponse('Hello World! for Lingcao')

def getItemOfImageObject(request):
    ''' get one available item: image, and return image_name '''
    image_info = {'image_name': None,
                  'image_center_latlon': None}

    # get the first available image_name (haven't been validated, less than 1 person is working on that)
    avail_image_name = get_available_image()
    if avail_image_name is None:
        pass

    return HttpResponse('getItemOfImageObject at %s'%str(datetime.now()))

def getImageFile(request,image_name):
    '''get the PNG file for an image '''
    one_record, b_success = get_one_record(image_name)    #
    if b_success is False:
        return one_record
    return FileResponse(open(one_record.image_path, 'rb'))

def getImageBound(request,image_name):
    '''get the image bounding box (geojson) for an image'''
    one_record, b_success = get_one_record(image_name)    #
    if b_success is False:
        return one_record
    with open(one_record.image_bound_path) as f_obj:
        data = json.load(f_obj)
    return JsonResponse(data)

def getImageObjects(request,image_name):
    '''get the objects on the image'''
    one_record, b_success = get_one_record(image_name)    #
    if b_success is False:
        return one_record
    with open(one_record.image_object_path) as f_obj:
        data = json.load(f_obj)
    return JsonResponse(data)