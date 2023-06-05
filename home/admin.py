from django.contrib import admin
from .models import CustomUserModel, Tag, Task
# Register your models here.

admin.site.register(CustomUserModel)
admin.site.register(Tag)
admin.site.register(Task)