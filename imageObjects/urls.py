from django.urls import path

from . import views
urlpatterns = [
    # ex: /imageObjects/
    path('',views.index, name='index'),
    # ex: /imageObjects/getitem
    path('getitem',views.getItemOfImageObject, name='getItemOfImageObject'),
    # ex: /imageObjects/username/getitem
    path('<str:user_name>/getitem',views.getItemOfImageObject_user, name='getItemOfImageObject_user'),
    # ex: /imageObjects/(str)/imagefile
    path('<str:user_name>/previous/<str:image_name>',views.getPreviousImageObject_user, name='getItemOfImageObject_user'),
    path('<str:image_name>/imagefile',views.getImageFile, name='getImageFile'),
    path('<str:image_name>/imagebound',views.getImageBound, name='getImageBound'),
    path('<str:image_name>/imageobject',views.getImageObjects, name='getImageObjects'),
    path('<str:user_name>/imageobject/<str:image_name>',views.getEditedObjects, name='getImageObjects'),
    # user submit a result, post request
    path('<str:user_name>/submitImageObjects',views.submitImageObjects, name='submitImageObjects'),
    path('<str:user_name>/savePolygons/<str:image_name>',views.savePolygons, name='savePolygons')
]