from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from segranks.views import ProjectListView, AnnotateView, AboutView

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^projects/$', ProjectListView.as_view(), name="ranks.views.projectlistview"),
    url(r'^projects/(?P<pk>\d+)/$', AnnotateView.as_view(), name="ranks.views.annotateview"),
    url(r'^about/', AboutView.as_view()),
)
