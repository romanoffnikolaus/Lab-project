from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Profile
from . import views


class UserTest(APITestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email = 'pimp@gmail.com',
            username = 'username',
            first_name = 'name',
            last_name = 'last_name',
            password = 'pimp',
            is_active = True
        )
        profile = [Profile(user=self.user, language = 'En')]
        Profile.objects.bulk_create(profile)

    def test_register(self):
        data = {
            'email':'new_user@gmail.com',
            'password': '5432',
            'password_confirm':'5432',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'username':'test_username'
        }
        request = self.factory.post('register/', data, format='json')
        view = views.RegistrationView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert User.objects.filter(email = data['email']).exists()

    def test_login(self):
        data = {
            'email': 'pimp@gmail.com',
            'password': 'pimp',
            'username': 'username'
        }
        request = self.factory.post('login/', data, format = 'json')
        view = TokenObtainPairView.as_view()
        response = view(request)
        assert response.status_code == 200

    def test_change_password(self):
        data = {
            'old_password':'pimp',
            'new_password': '1234',
            'new_password_confirm': '1234'
        }
        request = self.factory.post('change_password/', data, format='json')
        force_authenticate(request, user=self.user)
        view= views.ChangePasswordView.as_view()
        response = view(request)
        assert response.status_code == 200

        email = self.user.email
        data = {
            'email': email,
            'password': '1234',
            'username': 'username'
        }
        request = self.factory.post('login/', data, format = 'json')
        view = TokenObtainPairView.as_view()
        response = view(request)
        assert response.status_code == 200

    def test_change_password_pass(self):
        data = {
            'old_password':'pimp',
            'new_password': '12345',
            'new_password_confirm': '1234'
        }
        request = self.factory.post('change_password/', data, format='json')
        force_authenticate(request, user=self.user)
        view= views.ChangePasswordView.as_view()
        response = view(request)
        assert response.status_code == 400
        assert response.data['non_field_errors'][0] == 'Пароли не совпадают!'
    
    def test_change_password_pass(self):

        data = {
            'old_password':'uncorrect_password',
            'new_password': '1234',
            'new_password_confirm': '1234'
        }
        request = self.factory.post('change_password/', data, format='json')
        force_authenticate(request, user=self.user)
        view= views.ChangePasswordView.as_view()
        response = view(request)
        assert response.status_code == 400
        assert response.data['old_password'][0] == 'Введен некорректный пароль'

    def test_forgot_password(self):
        data = {
            'email':'pimp@gmail.com'
        }
        request = self.factory.post('forgot-password/', data, format='json')
        force_authenticate(request, user=self.user)
        view = views.ForgotPasswordView.as_view()
        response = view(request)
        assert response.data == 'Вам выслали сообщение для восстановления пароля'

    def test_forgor_password_complete(self):

        email = self.user.email
        user = User.objects.get(email=email)
        data_2 = {
            'email': 'pimp@gmail.com',
            'password': 'passw',
            'password_confirm': 'passw',
            'code': user.activation_code
        }
        request = self.factory.post('forgot_password_complete/', data_2, format='json')
        force_authenticate(request, user=self.user)
        view = views.ForgotPasswordCompleteView.as_view()
        response = view(request)
        assert response.status_code == 200 and response.data == 'Ваш пароль успешно восстановлен'

    def test_forgor_password_complete_pass(self):
        email = self.user.email
        user = User.objects.get(email=email)
        data_2 = {
            'email': 'pimp@gmail.com',
            'password': 'pass',
            'password_confirm': 'passw',
            'code': user.activation_code
        }
        request = self.factory.post('forgot_password_complete/', data_2, format='json')
        force_authenticate(request, user=self.user)
        view = views.ForgotPasswordCompleteView.as_view()
        response = view(request)
        assert response.status_code == 400
        assert response.data['non_field_errors'][0] == 'Пароли не совпадают'

    def test_forgor_password_complete_code(self):
        email = self.user.email
        user = User.objects.get(email=email)
        data_2 = {
            'email': 'pimp@gmail.com',
            'password': 'passw',
            'password_confirm': 'passw',
            'code': 'fhbjhdfb'
        }
        request = self.factory.post('forgot_password_complete/', data_2, format='json')
        force_authenticate(request, user=self.user)
        view = views.ForgotPasswordCompleteView.as_view()
        response = view(request)
        assert response.status_code == 400
        assert response.data['non_field_errors'][0] == 'Пользователь не найден или введен неправильный код'

    def test_logout(self):
        request = self.factory.post('logout/')
        force_authenticate(request, user=self.user)
        view = views.APILogoutView.as_view()
        response = view(request)
        assert response.data == 'Всего доброго!'

    def test_create_profile(self):
        self.user = User.objects.create_user(
            email = 'case@gmail.com',
            username = 'case_user',
            first_name = 'name',
            last_name = 'last_name',
            password = 'pimp',
            is_active = True
        )
        data = {
        "competence": "Some competence",
        "language": "En",
        "site_url": "https://example.com",
        "twitter_url": "https://twitter.com/",
        "facebook_url": "https://www.facebook.com/example",
        "linkedin_url": "https://www.linkedin.com/in/Krutoy",
        "youtube_url": "https://www.youtube.com/@example",
        "is_hidden": False,
        "is_hidden_courses": False,
        "promotions": False,
        "mentor_ads": False,
        "email_ads": False
        }
        request = self.factory.post('profile/', data, format='json')
        force_authenticate(request, user=self.user)
        view = views.ProfileView.as_view({'post': 'create'})
        response = view(request)
        assert response.status_code == 201
        assert response.data['language'] == data['language'] == 'En'

    def test_delete_unauthorized(self):
        user = User.objects.all()[0]
        id = Profile.objects.all()[0].id
        request = self.factory.delete(f'profile/{id}/')
        view = views.ProfileView.as_view({'delete': 'destroy'})
        response = view(request, pk=id)
        assert response.status_code == 401


    def test_retrieve(self):
        user = User.objects.all()[0]
        slug = Profile.objects.all()[0].id
        request = self.factory.delete(f'profile/{slug}')
        force_authenticate(request, user=user)
        view = views.ProfileView.as_view({'delete':'destroy'})
        response = view(request, pk=slug)
        print(response.data)
        assert response.status_code == 204
    
    def test_partial_update(self):
        user = User.objects.all()[0]
        profile = Profile.objects.all()[0].id
        data = {
        "competence": "Some competence",
        "language": "Ru",
        }
        request = self.factory.patch(f'profile/{profile}',data,format='json')
        force_authenticate(request, user=user)
        view = views.ProfileView.as_view({'patch':'partial_update'})
        response = view(request, pk=profile)
        assert response.status_code == 200
        assert response.data['language'] == data['language'] == 'Ru'