import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create_user(username='Test_name')
        cls.group = Group.objects.create(
            title='test_name_group',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            text='test_text_form',
            author=cls.author,
            group=cls.group,
        )
        cls.form = PostForm()
        cache.clear()
        cls.url_create = reverse('posts:post_create')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_with_picture(self):
        """Валидная форма создает запись с картинкой"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.author,
                text='Тестовый текст'
            ).exists()
        )

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
