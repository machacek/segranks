from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from django.contrib import admin
admin.autodiscover()

from segranks.views import ProjectListView, AnnotateView, AboutView, RegistrationView, SubmitView

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', RegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', ProjectListView.as_view(), name="segranks.views.projectlistview"),
    url(r'^project-(?P<pk>\d+)/$', login_required(AnnotateView.as_view()), name="segranks.views.annotateview"),
    url(r'^project-(?P<pk>\d+)/submit/$', login_required(SubmitView.as_view()), name="segranks.views.submitview"),
    url(r'^about/', AboutView.as_view(), name="segranks.views.aboutview"),
)
