from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='Test_for_post',
        )
        cls.author_for_post = User.objects.create_user(
            username='Test_name',
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
        cls.post_for_test = Post.objects.create(
            author=cls.author_for_post,
            text='Текст для проверки редактирования',
            group=cls.group,
        )
        cls.url_names_guest = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }
        cls.url_names_authorized = {
            '/create/': 'posts/post_create.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/post_create.html',
        }
        cls.merged_dict = {
            **cls.url_names_guest,
            **cls.url_names_authorized,
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_client_test = Client()
        self.authorized_client_test.force_login(self.author_for_post)

    def test_urls_exists_guest(self):
        """Доступность страниц любому пользователю."""
        for url_adress in self.url_names_guest:
            with self.subTest(url_address=url_adress):
                response = self.client.get(url_adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_authorized(self):
        """Доступность страниц авторизованному пользователю."""
        for url_adress in self.merged_dict:
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

    def test_urls_correct_template_404(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница (ошибка 404)
        доступна любому пользователю.
        """
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_not_author(self):
        """Страница редактирования сообщения доступна
        только автору, не автор перенаправляется на детали поста.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post_for_test.id}/edit/',
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post_for_test.id}/',
            HTTPStatus.FOUND,
        )
