from django.forms import ModelForm
from django import forms

# from .models import UserInput
# from .models import Image

# #
# class UserInputForm(ModelForm):
#     class Meta:
#         model = UserInput
#         # image_name is a ForeignKey, it actually is image_name_id in database,
#         # when we submit a POST request, we need to send image_name_id (int), making things complicated
#         fields = ['image_name']  # 'user_name' # 'user_image_output' is a filePath, end in "Error", file not exist

# class imageObjectForm(ModelForm):
#     class Meta:
#         model = Image
#         fields = ['image_name','concurrent_count','image_valid_times']

class submitObjectForm(forms.Form):
    image_name = forms.CharField(label='image_name', max_length=100)
    possibility = forms.CharField(label='possibility', max_length=100)
    user_note = forms.CharField(label='user_note', max_length=4000)
