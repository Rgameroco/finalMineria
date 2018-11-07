from django.contrib import admin
from apps.movies.models import *

admin.site.register(Movie)
admin.site.register(Link)
admin.site.register(Tag)
admin.site.register(Rating)