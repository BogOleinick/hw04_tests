from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTest.post
        expected = post.text[:15]
        self.assertEqual(expected, str(post))

    def test_models_have_title(self):
        """Проверяем, что у модели group корректно работает __str__"""
        group = PostModelTest.group
        expected = group.title
        self.assertEqual(expected, str(group))

    def test_models_have_verbose_name_group(self):
        """Проверяем, что у модели group корректно работает verbose_name."""
        group = PostModelTest.group
        verbose_field = {
            'title': 'Название группы',
            'slug': 'Адрес для страницы с группой',
            'description': 'Описание'
        }
        for field, expected_value in verbose_field.items():
            with self.subTest(field=field):
                self.assertEqual(group._meta.get_field(
                    field).verbose_name, expected_value)

    def test_models_have_verbose_name_post(self):
        """Проверяем, что у модели post корректно работает verbose_name."""
        post = PostModelTest.post
        verbose_field = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in verbose_field.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(
                    field).verbose_name, expected_value)

    def test_models_have_hepl_text_post(self):
        """Проверяем, что у модели post корректно работает hepl_text."""
        post = PostModelTest.post
        hepl_text = {
            'text': 'Введите текст поста',
            'pub_date': 'Дата публикации поста',
            'author': 'Введите имя автора',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in hepl_text.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(
                    field).help_text, expected_value)

    def test_models_have_hepl_text_group(self):
        """Проверяем, что у модели group корректно работает hepl_text."""
        group = PostModelTest.group
        hepl_text = {
            'title': 'Введите название группы',
            'slug': 'Введите адрес для страницы с группой',
            'description': 'Введите описание группы'
        }
        for field, expected_value in hepl_text.items():
            with self.subTest(field=field):
                self.assertEqual(group._meta.get_field(
                    field).help_text, expected_value)
