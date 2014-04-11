from django.contrib import admin

from segranks.models import RankProject, Sentence, Segment, Annotation

admin.site.register(RankProject)
admin.site.register(Sentence)
admin.site.register(Segment)
admin.site.register(Annotation)
