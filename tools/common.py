from django.http import HttpResponse
from imageObjects.models import Image
from django.contrib.auth.models import User
from imageObjects.models import UserInput
from django.utils import timezone as datetime
from datetime import timedelta

import imageObjects.views as  views

def get_one_record_image(image_name):
    # query = Image.objects.get(image_name=image_name)    # will raise DoesNotExist if not exist
    query = Image.objects.filter(image_name=image_name)  #
    if len(query) < 1:
        return HttpResponse('%s not in the image database' % image_name, status=404), False
    elif len(query) > 1:
        return HttpResponse('multiple %s in the image database' % image_name, status=300), False
    else:
        return query[0], True

def get_one_record_user(user_name):
    query = User.objects.filter(username=user_name)  #
    if len(query) < 1:
        return HttpResponse('%s not in the user database' % user_name, status=404), False
    elif len(query) > 1:
        return HttpResponse('multiple %s in the user database' % user_name, status=300), False
    else:
        return query[0], True

def get_one_record_userInput(user_name,image_name):
    user_name_id = get_user_id(user_name)
    if user_name_id is None:
        return HttpResponse('%s not in the user database' % user_name, status=404), False
    image_id = get_image_id(image_name)
    if image_id is None:
        return HttpResponse('%s not in the image database' % image_name, status=404), False

    query = UserInput.objects.filter(user_name_id=user_name_id, image_name_id=image_id)
    if len(query) < 1:
        return HttpResponse('%s input on image: %s is not in the userinput database' % (user_name,image_name), status=404), False
    elif len(query) > 1:
        return HttpResponse('multiple userInput: %s-%s in the userinput database' % (user_name,image_name), status=300), False
    else:
        return query[0], True

def get_user_id(user_name):
    if User.objects.filter(username=user_name).exists():
        user_name_id = User.objects.get(username=user_name).id  # username is unqiue
        return user_name_id
    else:
        views.logger.error('User: %s does not exist' % user_name)
        return None

def get_image_id(image_name):
    query = Image.objects.filter(image_name=image_name)
    if len(query)==1:
        return query[0].id
    elif len(query) < 1:
        views.logger.error('Image: %s does not exist' % image_name)
        return None
    else:
        views.logger.error('%d Image have the same name' % len(query))
        return None

def get_available_image(user_name=None,max_valid_times = 3 ):
    if user_name is None:
    # find images that image_valid_times < 3 and concurrent_count<3
    #     query = Image.objects.filter(image_valid_times__lte=max_valid_times).\
    #         filter(concurrent_count__lte=max_valid_times).order_by('image_name')  #
        views.logger.error('User is None')
        return None
    else:
        user_name_id = get_user_id(user_name)
        if user_name_id is None:
            return None
        # print('\n user_name_id:',user_name_id)
        query_user = UserInput.objects.filter(user_name_id = user_name_id)
        # to make sure the user dont work on the same image
        checked_image_ids = [item.image_name_id for item in query_user]
        # print('\n checked_image_ids \n',checked_image_ids)
        query = Image.objects.filter(image_valid_times__lt=max_valid_times). \
            filter(concurrent_count__lt=max_valid_times).\
            exclude(id__in=checked_image_ids).order_by('image_name')  # id__not_in not works, use exclude

    # for record in query:
    #     print(record.image_name, record.concurrent_count,record.image_valid_times)
    # remove records that image_valid_times + concurrent_count > 3
    sel_query = [ item for item in query if item.image_valid_times + item.concurrent_count < max_valid_times ]
    if len(sel_query) < 1:
        return None

    return sel_query[0].image_name

def get_previous_item(user_name,current_image):
    # get previous image that a user submitted, user_name is required
    user_name_id = get_user_id(user_name)
    if user_name_id is None:
        return None
    current_image_id = get_image_id(current_image)
    if current_image_id is None:
        return None

    # all input from the user
    query_user = UserInput.objects.filter(user_name_id=user_name_id)
    if len(query_user) < 1:
        return None

    # to make sure the user dont work on the same image
    checked_image_ids = [item.image_name_id for item in query_user]
    checked_image_ids = sorted(checked_image_ids)
    current_idx = checked_image_ids.index(current_image_id)
    if current_idx == 0:
        # previous_image_id = checked_image_ids[0]
        return None  # current one is the first one
    else:
        previous_image_id = checked_image_ids[current_idx-1]
        rec_img = Image.objects.filter(id=previous_image_id)[0]
        rec_input = UserInput.objects.filter(image_name_id=previous_image_id)[0]
        return rec_img.image_name, rec_input.possibility, rec_input.user_note, rec_input.user_image_output

def remove_invalid_userinput(max_period_h=12):
    # remove incomplete records older than max_period_h hours
    old_time = datetime.now() - timedelta(hours = max_period_h)
    # deleted, _rows_count = UserInput.objects.filter(possibility=None).filter(init_time__lt = old_time).delete()
    # print('deleted, _rows_count:', deleted, _rows_count)
    invalid_qs = UserInput.objects.filter(possibility=None).filter(init_time__lt = old_time)

    for qs in invalid_qs:
        user_input_rec = UserInput.objects.get(id=qs.id)
        image_rec = Image.objects.get(id=user_input_rec.image_name_id)
        user_input_rec.delete()
        image_rec.concurrent_count -= 1
        image_rec.save()
    if len(invalid_qs) > 0:
        views.logger.info('Deleted %d invalid userInput records' % len(invalid_qs))

def update_concurrent_count(max_valid_times=3, max_period_h=12):
    # # set the concurrent count for image has been completed as 0
    # row_count = Image.objects.filter(image_valid_times__gte=max_valid_times).\
    #                         filter(concurrent_count__gt=0).update(concurrent_count=0)  # set as 0
    # print('Set concurrent_count of %d records to 0' % row_count)

    # calculate the concurrent_count again
    input_qs = UserInput.objects.filter(possibility=None)
    if len(input_qs) > 0:
        image_ids = list(input_qs.values_list('image_name_id',flat=True)) # .distinct()
        for id in set(image_ids):
            qs = Image.objects.get(id=id)
            qs.concurrent_count = image_ids.count(id)
            qs.save()


def calculate_user_contribution(user_name):
    if user_name is None:
        return None,None,None,None
    # statics user input
    if User.objects.filter(username=user_name).exists():
        user_name_id = User.objects.get(username=user_name).id  # username is unqiue
    else:
        views.logger.error('User: %s does not exist' % user_name)
        return None,None,None,None
    total_count = Image.objects.count()     # total image count
    # output input from each user
    q_saved = UserInput.objects.exclude(possibility=None)
    unique_user_ids = list(q_saved.values_list('user_name_id',flat=True).distinct())
    # print('unique_user_ids:',unique_user_ids)
    total_user = len(unique_user_ids)
    # total_save = q_saved.count()
    select_user_contri = q_saved.filter(user_name_id=user_name_id).count()
    if select_user_contri > 0:
        unique_user_ids.remove(user_name_id)
    else:
        return total_count, select_user_contri, total_user, None

    other_contribute = {}
    other_contribute_list = []
    for user_id in unique_user_ids:
        count = q_saved.filter(user_name_id = user_id).count()
        other_contribute[user_id] = count
        other_contribute_list.append(count)
    # get rank
    other_contribute_list = sorted(other_contribute_list,reverse=True) # from large to small
    # print(other_contribute_list)
    rank = 1
    for idx, num in enumerate(other_contribute_list):
        if select_user_contri < num:
            rank = idx + 1

    # total image count,  user contribute count, total number of users with contribution,  rank.
    return total_count, select_user_contri, total_user, rank


if __name__ == '__main__':
    pass