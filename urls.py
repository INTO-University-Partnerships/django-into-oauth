from django.conf.urls import patterns, url

from oauth2_provider.views import TokenView

from .views import AuthorizationView, UserDataView, oauth2_logout


urlpatterns = patterns(
    '',
    url(r'^authorize/$', AuthorizationView.as_view(), name='authorize'),
    url(r'^token/$', TokenView.as_view(), name='token'),
    url(r'^user/$', UserDataView.as_view(), name='userdata'),
    url(r'^logout/$', oauth2_logout, name='oauth2_logout')
)
