from django.contrib import admin
from .models import UserProfile, Follow, Activity

admin.site.register(UserProfile)
admin.site.register(Follow)
admin.site.register(Activity)
