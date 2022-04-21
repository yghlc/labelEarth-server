from django.http import HttpResponse
from imageObjects.models import Image
from django.contrib.auth.models import User
from imageObjects.models import UserInput

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

def get_available_image(user_name=None):
    # each image should only be valided less than 3 times.
    max_valid_times = 3

    if user_name is None:
    # find images that image_valid_times < 3 and concurrent_count<3
        query = Image.objects.filter(image_valid_times__lte=max_valid_times).\
            filter(concurrent_count__lte=max_valid_times).order_by('image_name')  #
    else:
        if User.objects.filter(username=user_name).exists():
            user_name_id = User.objects.get(username=user_name).id  # username is unqiue
        else:
            views.logger.error('User: %s does not exist'%user_name)
            return None
        # print('\n user_name_id:',user_name_id)
        query_user = UserInput.objects.filter(user_name_id = user_name_id)
        # to make sure the user dont work on the same image
        checked_image_ids = [item.image_name_id for item in query_user]
        # print('\n checked_image_ids \n',checked_image_ids)
        query = Image.objects.filter(image_valid_times__lte=max_valid_times). \
            filter(concurrent_count__lte=max_valid_times).\
            exclude(id__in=checked_image_ids).order_by('image_name')  # id__not_in not works, use exclude

    # for record in query:
    #     print(record.image_name, record.concurrent_count,record.image_valid_times)
    # remove records that image_valid_times + concurrent_count > 3
    sel_query = [ item for item in query if item.image_valid_times + item.concurrent_count <= max_valid_times ]
    if len(sel_query) < 1:
        return None

    return sel_query[0].image_name




if __name__ == '__main__':
    pass