from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse


class TestsStaticViews(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_namespace(self):
        """Тестирование namespace author и tech."""
        template_name = [
            'about:author',
            'about:tech',
        ]
        for addres_name in template_name:
            with self.subTest(addres_name):
                response = self.guest_client.get(reverse(addres_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_address_to_template(self):
        """Тестируем вызов шаблона по адресу."""
        template_name = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for url, template in template_name.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse(url))
                self.assertTemplateUsed(response, template)
