from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class UsersViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_client = Client()
        cls.author = User.objects.create_user(
            username='Test_name',
            email='test@gmail.com',
        )
        cls.author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Ж',
            description='Тестовое описание группы',
            slug='zh',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.user = User.objects.create_user(
            username='john',
            email='john@doe.com',
            password='123abcdef'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_namespace(self):
        """Тестирование namespace users."""
        template_name = [
            'users:logout',
            'users:signup',
        ]
        for addres_name in template_name:
            with self.subTest(addres_name):
                response = self.authorized_client.get(reverse(addres_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_used_correct_templates(self):
        template_pages = {
            'users:logout': 'users/logged_out.html',
            'users:signup': 'users/signup.html',
        }
        for name, template in template_pages.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse(name))
                self.assertTemplateUsed(response, template)


class TestsStaticViews(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_namespace(self):
        """Тестирование namespace users."""
        template_name = [
            'users:password_reset_complete',
            'users:password_reset_done',
            'users:password_reset',
            'users:login',
            'users:signup',
        ]
        for addres_name in template_name:
            with self.subTest(addres_name):
                response = self.guest_client.get(reverse(addres_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_used_correct_templates(self):
        template_pages = {
            'users:password_reset_complete':
                'users/password_reset_complete.html',
            'users:password_reset_done':
                'users/password_reset_done.html',
            'users:password_reset':
                'users/password_reset_form.html',
            'users:login':
                'users/login.html',
            'users:signup':
                'users/signup.html',
        }
        for name, template in template_pages.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
