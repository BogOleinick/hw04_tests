from django.test import TestCase, Client
from posts.models import Group, Post, User

from http import HTTPStatus


class UsersUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='Test_name',
            email='test@gmail.com',
            password='password',
        )
        cls.group = Group.objects.create(
            title='ж',
            description='Тестовое описание',
            slug='zh',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_names_guest = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset.html',
            '/auth/password_reset/done/': 'users/password_reset/done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm/.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        self.url_names_authorized = {
            '/auth/logout/': 'users/logged_out.html',
        }
        self.url_names_redirected = {
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change/done/': 'users/password_change/done/.html',
        }

    def test_urls_exists_guest(self):
        """Доступность страниц любому пользователю."""
        for url_adress in self.url_names_guest:
            with self.subTest(address=url_adress):
                response = self.guest_client.get(url_adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_authorized(self):
        """Доступность страниц авторизованному пользователю."""
        for url_adress in self.url_names_authorized:
            with self.subTest(address=url_adress):
                response = self.authorized_client.get(url_adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_authorized(self):
        for url_adress in self.url_names_redirected:
            with self.subTest(address=url_adress):
                response = self.authorized_client.get(url_adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
