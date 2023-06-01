
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post, User


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(
            username='Test_name',
            email='test@gmail.com',
        )
        cls.group = Group.objects.create(
            title='Первая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_for_test = Group.objects.create(
            title='Вторая группа',
            slug='test_slug_second',
            description='Тестовое описание второй группы',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост",
            group=cls.group,
            image=cls.uploaded
        )
        cls.post_create_urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile', kwargs={'username': cls.author.username}):
                    'posts/profile.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}):
                    'posts/group_list.html',
        }
        cls.template_page_name = {
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.pk}):
                    'posts/post_detail.html',
            reverse(
                'posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.pk}):
                    'posts/post_create.html',
            **cls.post_create_urls,
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """Проверка шаблонов."""
        for reverse_name, template in self.template_page_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def assert_post(self, post_object):
        """Функция проверки контекста"""
        with self.subTest(post=post_object):
            self.assertEqual(
                post_object.author, self.post.author)
            self.assertEqual(
                post_object.id, self.post.id)
            self.assertEqual(
                post_object.group, self.post.group)
            self.assertEqual(
                post_object.text, self.post.text)

    def test_index_page_show_correct_context(self):
        """Проверка index с правильным ли context."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assert_post(response.context['page_obj'][0])
        img = Post.objects.first().image
        self.assertEqual(img, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Проверка group_list с правильным ли context."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(response.context['group'], self.group)
        self.assert_post(response.context['page_obj'][0])
        img = Post.objects.first().image
        self.assertEqual(img, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Проверка profile с правильным ли context."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author}
            )
        )
        self.assertEqual(response.context['author'], self.author)
        self.assert_post(response.context['page_obj'][0])
        img = Post.objects.first().image
        self.assertEqual(img, 'posts/small.gif')

    def test_detail_page_show_correct_context(self):
        """Проверка post_detail с правильниым ли context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assert_post(response.context['post'])
        img = Post.objects.first().image
        self.assertEqual(img, 'posts/small.gif')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(form, PostForm)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertTrue(response.context.get('is_edit'))

    def test_index_cache(self):
        """Тестирование кэша главной страницы."""
        first = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.get()
        post.text = 'Измененный текст'
        post.save()
        second = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first.content, second.content)
        cache.clear()
        third = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first.content, third.content)


class NewPostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='Test_name',
            email='test@gmail.com',
            password='password',
        )
        cls.group = Group.objects.create(
            title='Первая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_test_correct_entry = Group.objects.create(
            title='Вторая группа',
            slug='test_slug_two',
            description='Описание второй группы'
        )
        cls.new_post = Post.objects.create(
            author=cls.author,
            text='Новый пост 2',
            group=cls.group,
        )
        cls.post_create_urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile', kwargs={'username': cls.author.username}):
                    'posts/profile.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}):
                    'posts/group_list.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_new_post_is_shown(self):
        """Проверьте, что если при создании поста указать группу,
        то этот пост появляется в необходимых местах
        """
        for url in self.post_create_urls:
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertIn(self.new_post, response.context['page_obj'])

    def test_new_post_for_your_group(self):
        """Проверка, что этот пост не попал в группу,
        для которой не был предназначен.
        """
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={
                'slug': self.group_test_correct_entry.slug
            })
        )
        self.assertNotIn(self.new_post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.posts_on_first_page = settings.NUMBER_POSTS
        cls.posts_on_second_page = settings.NUMBER_POSTS_TEST_3_PAGE
        for i in range(cls.posts_on_second_page + cls.posts_on_first_page):
            Post.objects.create(
                text=f'Пост №{i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_page in url_pages:
            with self.subTest(reverse_page=reverse_page):
                self.assertEqual(len(self.guest_client.get(
                    reverse_page).context.get('page_obj')),
                    self.posts_on_first_page
                )
                self.assertEqual(len(self.guest_client.get(
                    reverse_page + '?page=2').context.get('page_obj')),
                    self.posts_on_second_page
                )


class FollowTest(TestCase):
    def setUp(self):
        self.follower = Client()
        self.following = Client()
        self.follower_user = User.objects.create(username='follower')
        self.following_user = User.objects.create(username='following')
        self.post = Post.objects.create(
            author=self.following_user,
            text='Тестовый текст',
        )
        self.follower.force_login(self.follower_user)
        self.following.force_login(self.following_user)

    def test_follow_func(self):
        self.follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following_user.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow_func(self):
        self.follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following_user.username},
            )
        )
        self.follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.following_user.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_sub_news_feed(self):
        Follow.objects.create(
            user=self.follower_user,
            author=self.following_user,
        )
        responce = self.follower.get('/follow/')
        self.assertEqual(
            responce.context['page_obj'][0].text, 'Тестовый текст'
        )
        self.assertNotEqual(
            self.following.get('/follow/'), 'Тестовый текст'
        )

    def test_comment_func(self):
        self.following.post(
            f'/posts/{self.post.pk}/comment/',
            {'text': 'Первый комментарий'},
            follow=True
        )
        self.assertContains(
            self.following.get(f'/posts/{self.post.pk}/'),
            'Первый комментарий',
        )
        self.following.logout()
        self.following.post(
            f'/posts/{self.post.pk}/comment/',
            {'text': 'Комментарий клиента'},
            follow=True)
        self.assertNotContains(
            self.following.get(f'/posts/{self.post.pk}/'),
            'Комментарий клиента',
        )
