from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from segranks.views import ProjectListView, AnnotateView, AboutView

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^$', ProjectListView.as_view(), name="segranks.views.projectlistview"),
    url(r'^project-(?P<pk>\d+)/$', AnnotateView.as_view(), name="segranks.views.annotateview"),
    url(r'^about/', AboutView.as_view(), name="segranks.views.aboutview"),
)
