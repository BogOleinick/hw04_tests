from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTests(TestCase):
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
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_names_guest = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        self.url_names_authorized = {
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.pk}/edit/': 'posts/post_create.html',
        }
        self.merged_dict = {
            **self.url_names_guest,
            **self.url_names_authorized,
        }

    def test_urls_exists_guest(self):
        """Доступность страниц любому пользователю."""
        for url_adress in self.url_names_guest:
            with self.subTest(address=url_adress):
                response = self.client.get(url_adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_authorized(self):
        """Доступность страниц авторизованному пользователю."""
        for url_adress in self.url_names_authorized:
            with self.subTest(address=url_adress):
                response = self.authorized_client.get(url_adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_guest(self):
        """Перенаправит анонимного пользователя на страницу логина.
        """
        for url_adress in self.url_names_authorized:
            with self.subTest(address=url_adress):
                response = self.client.get(
                    url_adress,
                    follow=True,
                )
                self.assertRedirects(
                    response, f'/auth/login/?next={url_adress}'
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Авторизованный пользователь.
        """
        for address, template in self.merged_dict.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница (ошибка 404)
        доступна любому пользователю.
        """
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
