from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Test_name')
        cls.group = Group.objects.create(
            title='test_name_group',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text_form',
            group=cls.group,
        )
        cls.url_create = reverse('posts:post_create')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_authorized_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form = {
            'text': self.post.text,
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form,
            follow=True
        )
        # Проверяем увеличилось ли число постов
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
        )
        # Проверяем создались ли запись
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.group.id,
            ).exists()
        )

    def test_guest_create_post(self):
        """Проверяем, при создании поста анонимом количество постов
        в базе данных не изменится.
        """
        posts_count = Post.objects.count()
        form = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, f'/auth/login/?next={self.url_create}')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.author,
            group=self.group,
        )
        form = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertTrue(post.text == form['text'])
        self.assertTrue(post.author == self.author)
        self.assertTrue(post.group_id == form['group'])
