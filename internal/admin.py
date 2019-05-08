from django.contrib import admin
from .models import Preference, Link, Event

admin.site.register(Preference)
admin.site.register(Link)
admin.site.register(Event)
