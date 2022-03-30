from django.http import HttpResponse
from imageObjects.models import Image

def get_one_record(image_name):
    # query = Image.objects.get(image_name=image_name)    # will raise DoesNotExist if not exist
    query = Image.objects.filter(image_name=image_name)  #
    if len(query) < 1:
        return HttpResponse('%s not in the database' % image_name, status=404), False
    elif len(query) > 1:
        return HttpResponse('multiple %s in the database' % image_name, status=300), False
    else:
        return query[0], True

def get_available_image(user_name=None):
    # find images that image_valid_times < 3 and concurrent_count<3
    query = Image.objects.filter(image_valid_times__lte=3).filter(concurrent_count__lte=3).order_by('image_name')  #
    # for record in query:
    #     print(record.image_name, record.concurrent_count,record.image_valid_times)
    # remove records that image_valid_times - concurrent_count <= 0
    sel_query = [ item for item in query if item.image_valid_times - item.concurrent_count > 0 ]
    if len(sel_query) < 1:
        return None
    else:
        return sel_query[0].image_name


if __name__ == '__main__':
    pass