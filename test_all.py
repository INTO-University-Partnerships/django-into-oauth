import json

from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.utils.encoding import force_str

import oauth2_provider

from .views import UserDataView, AuthorizationView
from .models import OauthSignOut

Application = oauth2_provider.models.get_application_model()
UserModel = get_user_model()


@skipIfCustomUser
class UserDataViewTestCase(TestCase):

    email = 'mike.mcgowan@into.uk.com'
    first_name = 'Mike'
    last_name = 'McGowan'
    username = 'Misiek'

    def setUp(self):
        self.user = UserModel.objects.create_user(
            username=self.username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name
        )
        self.user.is_active = True
        self.user.save()
        self.factory = RequestFactory()

    def tearDown(self):
        self.user.delete()

    def test_get_userdata(self):
        request = self.factory.get(reverse('oauth2_provider:userdata'))
        request.user = self.user

        view = UserDataView()
        view.request = request

        with self.settings(INTO_OAUTH_USERDATA={
            'emailaddress': 'email',
            'firstname': 'first_name',
            'lastname': 'last_name'
        }):
            response = view.get(request)
            self.assertEqual(response.status_code, 200)
            userdata = json.loads(force_str(response.content))
            self.assertEqual(self.last_name, userdata['lastname'])
            self.assertEqual(self.first_name, userdata['firstname'])
            self.assertEqual(self.email, userdata['emailaddress'])

        with self.settings(INTO_OAUTH_USERDATA={
            'Username': 'email',
            'user_last_name': 'last_name'
        }):
            response = view.get(request)
            self.assertEqual(response.status_code, 200)
            userdata = json.loads(force_str(response.content))
            self.assertEqual(self.last_name, userdata['user_last_name'])
            self.assertEqual(self.email, userdata['Username'])


@skipIfCustomUser
class AuthorizationViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.test_user = UserModel.objects.create_user(
            'test_user',
            'test@user.com',
            '123456'
        )

        self.application = Application(
            name='Test Into Application',
            redirect_uris="http://localhost",
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        oauth2_provider.settings._SCOPES = ['read', 'write']

    def tearDown(self):
        self.application.delete()
        self.test_user.delete()

    def test_authorize_redirect(self):
        url = reverse('oauth2_provider:authorize')
        authcode_data = {
            'client_id': self.application.client_id,
            'state': 'random_state_string',
            'redirect_uri': 'http://localhost',
            'response_type': 'code',
            'approval_prompt': 'skip'
        }
        request = self.factory.get(url, authcode_data)
        request.user = self.test_user
        view = AuthorizationView()
        view.request = request
        response = view.get(request)
        self.assertIn(authcode_data['redirect_uri'], response.url)
        self.assertIn('state=' + authcode_data['state'], response.url)
        self.assertIn('code=', response.url)
        self.assertEquals(302, response.status_code)


@skipIfCustomUser
class LogoutViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.test_user = UserModel.objects.create_user(
            'test_user',
            'test@user.com',
            '123456'
        )
        self.application1 = Application(
            name='Test Into Application',
            redirect_uris='http://localhost',
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            client_id='test_client_id_1'
        )
        self.application2 = Application(
            name='Test Into Application 2',
            redirect_uris='http://localhost/app2',
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            client_id='test_client_id_2'
        )
        self.application1.save()
        self.application2.save()
        self.signout1 = OauthSignOut.objects.create(
            application_id=self.application1.id,
            signout_uri='http://consumer-logout.uri'
        )
        self.signout2 = OauthSignOut.objects.create(
            application_id=self.application2.id,
            signout_uri='http://consumer-logout2.uri'
        )
        self.signout1.save()
        self.signout2.save()

    def tearDown(self):
        self.signout1.delete()
        self.signout2.delete()
        self.application1.delete()
        self.application2.delete()
        self.test_user.delete()

    def test_logout(self):
        response = self.client.get(reverse('oauth2_provider:oauth2_logout'))
        self.assertEquals(self.signout1.signout_uri, response.url)
        self.assertEquals(302, response.status_code)

    def test_logout_app1(self):
        response = self.client.get(
            reverse('oauth2_provider:oauth2_logout'),
            {'client_id': self.application1.client_id}
        )
        self.assertEquals(self.signout2.signout_uri, response.url)
        self.assertEquals(302, response.status_code)

    def test_logout_app2(self):
        response = self.client.get(
            reverse('oauth2_provider:oauth2_logout'),
            {'client_id': self.application2.client_id}
        )
        self.assertRedirects(response, settings.LOGIN_URL)
