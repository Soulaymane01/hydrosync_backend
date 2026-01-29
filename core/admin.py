from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Users)   # Has a problem  needs to be fixed 
admin.site.register(Assets)

