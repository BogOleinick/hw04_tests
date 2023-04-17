from django.test import TestCase, Client

from http import HTTPStatus


class AbottUrlTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls_names_template = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def testing_url_exists(self):
        for url_adress in self.urls_names_template:
            with self.subTest(url_adress):
                response = self.guest_client.get(url_adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def testing_correct_templates(self):
        for address, template in self.urls_names_template.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
