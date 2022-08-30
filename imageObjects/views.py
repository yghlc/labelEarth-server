from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.http import HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db import transaction

from imageObjects.forms import submitObjectForm
# from .forms import imageObjectForm

from imageObjects.models import Image
from imageObjects.models import UserInput
from tools.common import get_one_record_image
from tools.common import get_one_record_user
from tools.common import get_one_record_userInput
from tools.common import get_available_image
from tools.common import calculate_user_contribution
from tools.common import update_concurrent_count
from tools.common import remove_invalid_userinput
from tools.common import get_previous_item


max_valid_times = 3     # each image should only be valided less than 3 times.
max_work_period_h = 12  # when a user get an image, it should be submit results in 12 hours

from django.utils import timezone as datetime
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
    domain = request.build_absolute_uri('/')[:-1]
    login_url= domain + '/user/login'
    # return HttpResponse('Hello, please use additional terms to get or send data!')
    return HttpResponse('Hello, please <a href=%s>login (create an account if need)</a>, then start identifying thaw slumps!'%login_url)

def getItemOfImageObject(request):
    ''' get one available item: image, and return image_name '''
    return getItemOfImageObject_user(request,None)

def getItemOfImageObject_user(request,user_name):
    ''' get one available item: image, and return image_name '''
    image_info = {'image_name': None,
                  'image_center_lat': None,
                  'image_center_lon': None,
                  'image_count':None,
                  'contribution':None,
                  'total_user':None,
                  'user_rank':None}

    remove_invalid_userinput(max_period_h=max_work_period_h)
    # get the first available image_name (haven't been fully validated (<input's from the users))
    avail_image_name = get_available_image(user_name=user_name,max_valid_times=max_valid_times)
    if avail_image_name is not None:
        image_info['image_name'] = avail_image_name
        one_record, b_success = get_one_record_image(avail_image_name)
        if b_success is False:
            return one_record
        image_info['image_center_lat'] = one_record.image_cen_lat
        image_info['image_center_lon'] = one_record.image_cen_lon

        # create a record in UserInput(possibility=None), user and image has been checked in get_available_image
        user_rec, b_success = get_one_record_user(user_name)
        image_rec, b_success = get_one_record_image(avail_image_name)
        user_inpu_rec = UserInput(user_name=user_rec, image_name=image_rec,
                                  init_time=datetime.now(),possibility=None)
        user_inpu_rec.save()
    else:
        image_info['image_name'] = 'NotAvailable'
        image_info['image_center_lat'] = image_info['image_center_lon'] = 0
        # return HttpResponse('No available images for %s to work, Thank you!'%user_name)

    # calculate the concurrent_count for each item (has been got, but not completed)
    update_concurrent_count(max_valid_times=max_valid_times, max_period_h=max_work_period_h)

    # get user contribution
    total_count, user_contribute, total_user, user_rank = calculate_user_contribution(user_name)
    if total_count is not None:
        image_info['image_count'] = total_count
        image_info['contribution'] = user_contribute
        image_info['total_user'] = total_user
        image_info['user_rank'] = user_rank

    logger.info('user: %s request an image'%str(user_name))
    return JsonResponse(image_info)

def getPreviousImageObject_user(request,user_name,image_name):
    ''' get previous image that a user submitted,  and return image_name '''
    image_info = {'image_name': None,
                  'image_center_lat': None,
                  'image_center_lon': None,
                  'possibility':None,
                  'user_note':None,
                  'edit_polygons':None,
                  'image_count': None,
                  'contribution': None,
                  'total_user': None,
                  'user_rank': None}

    pre_image_name, possibility,user_note, edit_polygons = get_previous_item(user_name,image_name)
    print('pre_image_name, possibility,user_note:',pre_image_name, possibility,user_note)
    if pre_image_name is not None:
        image_info['image_name'] = pre_image_name
        one_record, b_success = get_one_record_image(pre_image_name)
        if b_success is False:
            return one_record
        image_info['image_center_lat'] = one_record.image_cen_lat
        image_info['image_center_lon'] = one_record.image_cen_lon
        if possibility is not None:
            image_info['possibility'] = possibility
        if user_note is not None:
            image_info['user_note'] = user_note
        if edit_polygons is not None and edit_polygons != 'test.geojson':
            image_info['edit_polygons'] = edit_polygons

        logger.info('user: %s got an image that has been checked previously' % str(user_name))
    else:
        image_info['image_name'] = 'NotAvailable'
        image_info['image_center_lat'] = image_info['image_center_lon'] = 0

    # get user contribution
    total_count, user_contribute, total_user, user_rank = calculate_user_contribution(user_name)
    if total_count is not None:
        image_info['image_count'] = total_count
        image_info['contribution'] = user_contribute
        image_info['total_user'] = total_user
        image_info['user_rank'] = user_rank

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

def getEditedObjects(request,user_name,image_name):
    '''get the polygons edited or added by a user for the image'''
    user_input_rec, b_success = get_one_record_userInput(user_name, image_name)
    if b_success is False:
        return user_input_rec
    geojson = os.path.join(BASE_DIR,user_input_rec.user_image_output)
    if os.path.exists(geojson) is False:
        logger.error('error: %s does not exist'%geojson)
        return HttpResponse('error: %s does not exist'%geojson)

    with open(geojson) as f_obj:
        data = json.load(f_obj)
    logger.info('request the user:%s added or edited polygons for %s' % (user_name,image_name))
    return JsonResponse(data)

# # csrf_exempt to remove the requiement of CSRF COOKIE
# @csrf_exempt
# def submitImageObjects(request,user_name):
#     '''submit object information for an image'''
#     # print('\n In submitImageObjects \n')
#     if request.method == 'POST':
#         # print('\n I just send a POST request \n')
#         # print('request.POST:',request.POST)
#         # logger.info('request.POST: %s',str(request.POST))
#         input_form = submitObjectForm(request.POST)
#         # print('input_form.is_valid()',input_form.is_valid())
#         logger.info('%s submit a POST request'%user_name)
#         if input_form.is_valid():
#             # print(input_form)     # it output a html string
#             image_name = input_form.cleaned_data['image_name']
#             possibility = input_form.cleaned_data['possibility']
#             user_note = input_form.cleaned_data['user_note']
#             # print('image_name after clean is:', image_name)
#             # save one record
#             user_rec, b_success = get_one_record_user(user_name)
#             if b_success is False:
#                 return user_rec
#             image_rec, b_success = get_one_record_image(image_name)
#             if b_success is False:
#                 return image_rec
#             # print("user_rec:",user_rec)
#             # print("image_rec:",image_rec)
#             if UserInput.objects.filter(user_name_id=user_rec.id, image_name_id=image_rec.id).exists():
#                 with transaction.atomic():
#                     user_inpu_rec = UserInput.objects.select_for_update().get(user_name_id=user_rec.id, image_name_id=image_rec.id)
#                     user_inpu_rec.save_time = datetime.now()
#                     # user_inpu_rec.user_image_output = 'test.geojson'
#                     user_inpu_rec.possibility = possibility
#                     user_inpu_rec.user_note = user_note
#                     user_inpu_rec.save()
#             else:
#                 # a record should be created when get an image
#                 logger.error('input with user: %s and image: %s does not exist' % (user_name, image_name))
#                 return HttpResponse('input with user: %s and image: %s does not exist' % (user_name, image_name))
#                 # user_inpu_rec = UserInput(user_name=user_rec,image_name=image_rec,
#                 #                       user_image_output='test.geojson',save_time=datetime.now(),
#                 #                       possibility=possibility,user_note=user_note)
#                 # user_inpu_rec.save()
#             # updated one record for images
#             with transaction.atomic():
#                 image_rec_update = Image.objects.select_for_update().get(image_name=image_name)
#                 image_rec_update.image_valid_times += 1
#                 image_rec_update.concurrent_count = max(image_rec_update.concurrent_count-1,0)
#                 image_rec_update.save()
#
#             # get the next image for user to check
#             # return HttpResponseRedirect(reverse('index'))
#             logger.info('success: save the input from %s for image: %s '%(user_name,image_name))
#             return HttpResponse('success: save the input from %s for image: %s '%(user_name,image_name))
#         else:
#             logger.error('Thank you, I got a POST request, but it is invalid')
#             return HttpResponse('Thank you, I got a POST request, but it is invalid')
#             # return HttpResponseRedirect(reverse('index'))
#     else:
#         pass
#
#     logger.info('Hello, this is submitImageObjects.')
#     return HttpResponse('Hello, this is submitImageObjects.')



# csrf_exempt to remove the requiement of CSRF COOKIE
@csrf_exempt
def submitImageObjects(request,user_name):
    '''submit object information for an image'''
    # print('\n In submitImageObjects \n')
    logger.info('%s call submitImageObjects ' % user_name)
    if request.method == 'POST':
        # print(request.body)
        try:
            data = json.loads(request.body)  # request.body is a string
        except Exception as e:
            logger.error('form data from user: %s json.loads: %s' % (user_name, e))
            return HttpResponse('form data, json.loads: error: %s' % e)

        logger.info('%s submit a POST request (form) via json string'%user_name)
        # logger.info(request.body)
        logger.info(str(data))
        if 'image_name' in data.keys() and 'possibility' in data.keys() and 'user_note' in data.keys():
            # print(input_form)     # it output a html string
            image_name = data['image_name']
            possibility = data['possibility']
            user_note = data['user_note']
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
            if UserInput.objects.filter(user_name_id=user_rec.id, image_name_id=image_rec.id).exists():
                with transaction.atomic():
                    user_inpu_rec = UserInput.objects.select_for_update().get(user_name_id=user_rec.id, image_name_id=image_rec.id)
                    user_inpu_rec.save_time = datetime.now()
                    # user_inpu_rec.user_image_output = 'test.geojson'
                    user_inpu_rec.possibility = possibility
                    user_inpu_rec.user_note = user_note
                    user_inpu_rec.save()
            else:
                # a record should be created when get an image
                logger.error('input with user: %s and image: %s does not exist' % (user_name, image_name))
                return HttpResponse('input with user: %s and image: %s does not exist' % (user_name, image_name))
                # user_inpu_rec = UserInput(user_name=user_rec,image_name=image_rec,
                #                       user_image_output='test.geojson',save_time=datetime.now(),
                #                       possibility=possibility,user_note=user_note)
                # user_inpu_rec.save()
            # updated one record for images
            with transaction.atomic():
                image_rec_update = Image.objects.select_for_update().get(image_name=image_name)
                image_rec_update.image_valid_times += 1
                image_rec_update.concurrent_count = max(image_rec_update.concurrent_count-1,0)
                image_rec_update.save()

            # get the next image for user to check
            # return HttpResponseRedirect(reverse('index'))
            logger.info('success: save the input from %s for image: %s'%(user_name,image_name))
            return HttpResponse('success: save the input from %s for image: %s'%(user_name,image_name))
        else:
            logger.error('Thank you, I got a POST request, but it is invalid')
            return HttpResponse('Thank you, I got a POST request, but it is invalid')
            # return HttpResponseRedirect(reverse('index'))
    else:
        pass

    logger.info('Hello, this is submitImageObjects.')
    return HttpResponse('Hello, this is submitImageObjects.')

@csrf_exempt
def savePolygons(request,user_name,image_name):
    '''save polygons user add or edit for an image to server'''
    # print('\n In savePolygons \n')
    if request.method == 'POST':
        # print(request.body)
        try:
            data = json.loads(request.body) # request.body is a string
        except Exception as e:
            logger.error('%s json.loads: %s'%(user_name,e))
            return HttpResponse('json.loads: error: %s'%e)

        # print('data:',data)
        logger.info('%s submit a POST request to save polygons' % user_name)
        # save to database
        rel_path = os.path.join('data','objectPolygons','%s_by_%s.geojson'%(image_name,user_name))
        save_file_path = os.path.join(BASE_DIR,rel_path)
        # replace the old file if it exists
        with open(save_file_path,'w') as f_obj:
            json.dump(data,f_obj)

        # save the file name to database
        with transaction.atomic():
            user_input_rec, b_success = get_one_record_userInput(user_name,image_name,b_update=True)
            if b_success is False:
                return user_input_rec
            user_input_rec.user_image_output = rel_path
            user_input_rec.save()

        logger.info('Saving polygons OK!')
        return HttpResponse('Saving polygons OK!')
    else:
        logger.info('This is savePolygons.')
        return HttpResponse('This is savePolygons.')
