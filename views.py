import json

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.conf import settings

from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views import AuthorizationView
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.models import get_application_model
from oauth2_provider.views.generic import ProtectedResourceView

from .models import OauthSignOut


Application = get_application_model()


class AuthorizationView(AuthorizationView):
    def get(self, request, *args, **kwargs):
        require_approval = request.GET.get('approval_prompt', oauth2_settings.REQUEST_APPROVAL_PROMPT)
        if require_approval != 'skip':
            return super(AuthorizationView, self).get(
                request=request, *args, **kwargs)

        try:
            scopes, credentials = self.validate_authorization_request(request)
            uri, headers, body, status = self.create_authorization_response(
                request=self.request, scopes=" ".join(scopes),
                credentials=credentials, allow=True)
            return HttpResponseRedirect(uri)

        except OAuthToolkitError as error:
            return self.error_response(error)


class UserDataView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):

        fields = settings.INTO_OAUTH_USERDATA

        userdata = {}
        for key in fields:
            userdata[key] = getattr(request.user, fields[key])

        return HttpResponse(
            json.dumps(userdata, ensure_ascii=False),
            content_type='application/json')


def oauth2_logout(request):
    # client ID optionally passed from consumer app
    # on which the user has logged out
    client_id = request.GET.get('client_id', '')
    # all applications that require sign-out
    signouts = OauthSignOut.objects.all().order_by('id')
    if client_id:
        current = signouts.get(application__client_id=client_id)
        signouts = signouts.filter(id__gt=current.id)
    # redirect to the next app requiring single-sign-out
    if signouts.exists():
        redirect = signouts.first().signout_uri
        return HttpResponseRedirect(redirect)
    # otherwise, just log out of Django
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)
