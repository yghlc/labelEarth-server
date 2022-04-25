from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.http import HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from imageObjects.forms import submitObjectForm
# from .forms import imageObjectForm

from imageObjects.models import Image
from imageObjects.models import UserInput
from tools.common import get_one_record_image
from tools.common import get_one_record_user
from tools.common import get_available_image

from datetime import datetime
import json

import logging
# for this one, __name__ is "imageObjects.views"  (set this logger in "setting")
logger = logging.getLogger(__name__)

import os
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.
def index(request):
    return HttpResponse('Hello, please use additional terms to get or send data! -Lingcao')

def getItemOfImageObject(request):
    ''' get one available item: image, and return image_name '''
    return getItemOfImageObject_user(request,None)

def getItemOfImageObject_user(request,user_name):
    ''' get one available item: image, and return image_name '''
    image_info = {'image_name': None,
                  'image_center_lat': None,
                  'image_center_lon': None}

    # get the first available image_name (haven't been fully validated (<input's from the users))
    avail_image_name = get_available_image(user_name=user_name)
    if avail_image_name is not None:
        image_info['image_name'] = avail_image_name
        one_record, b_success = get_one_record_image(avail_image_name)
        if b_success is False:
            return one_record
        image_info['image_center_lat'] = one_record.image_cen_lat
        image_info['image_center_lon'] = one_record.image_cen_lon
    else:
        return HttpResponse('No available images for %s to work, Thank you!'%user_name)

    logger.info('user: %s request an image'%str(user_name))
    return JsonResponse(image_info)

def getImageFile(request,image_name):
    '''get the PNG file for an image '''
    one_record, b_success = get_one_record_image(image_name)    #
    if b_success is False:
        return one_record
    logger.info('request the image file for %s' % image_name)
    return FileResponse(open(os.path.join(BASE_DIR,one_record.image_path), 'rb'))

def getImageBound(request,image_name):
    '''get the image bounding box (geojson) for an image'''
    one_record, b_success = get_one_record_image(image_name)    #
    if b_success is False:
        return one_record
    with open(os.path.join(BASE_DIR,one_record.image_bound_path)) as f_obj:
        data = json.load(f_obj)
    logger.info('request the Image Bound geojson for %s' % image_name)
    return JsonResponse(data)

def getImageObjects(request,image_name):
    '''get the objects on the image'''
    one_record, b_success = get_one_record_image(image_name)    #
    if b_success is False:
        return one_record
    with open(os.path.join(BASE_DIR,one_record.image_object_path)) as f_obj:
        data = json.load(f_obj)
    logger.info('request the Image Object geojson for %s' % image_name)
    return JsonResponse(data)

# csrf_exempt to remove the requiement of CSRF COOKIE
@csrf_exempt
def submitImageObjects(request,user_name):
    '''submit object information for an image'''
    # print('\n In submitImageObjects \n')
    if request.method == 'POST':
        # print('\n I just send a POST request \n')
        # print('request.POST:',request.POST)
        input_form = submitObjectForm(request.POST)
        # print('input_form.is_valid()',input_form.is_valid())
        if input_form.is_valid():
            # print(input_form)     # it output a html string
            image_name = input_form.cleaned_data['image_name']
            # print('image_name after clean is:', image_name)
            # save one record
            user_rec, b_success = get_one_record_user(user_name)
            if b_success is False:
                return user_rec
            image_rec, b_success = get_one_record_image(image_name)
            if b_success is False:
                return image_rec
            # print("user_rec:",user_rec)
            # print("image_rec:",image_rec)
            user_inpu_rec = UserInput(user_name=user_rec,image_name=image_rec,
                                      user_image_output='test.geojson',saving_time=datetime.now())
            user_inpu_rec.save()
            # updated one record for images
            image_rec.image_valid_times += 1
            # img = Image(image_name=image_name, image_path=image_path, image_bound_path=image_bound_path,
            #             image_object_path=image_object_path, concurrent_count=0, image_valid_times=0)
            image_rec.save()

            # get the next image for user to check
            return HttpResponseRedirect('getitem')
        else:
            return HttpResponse('Thank you, I got a POST request, but is invalid')
            # return HttpResponseRedirect(reverse('index'))
    else:
        pass

    return HttpResponse('Hello, this is submitImageObjects. -Lingcao')