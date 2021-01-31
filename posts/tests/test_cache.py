from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post


class CacheTest(TestCase):
    AUTH_USER = 'TestName'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(username=cls.AUTH_USER)
        Post.objects.create(text='Ляляля',
                            author=cls.user)

    def test_cache_index(self):
        self.guest_client = Client()
        response0 = self.guest_client.get(reverse('index'))
        Post.objects.create(text='Тестовый текст',
                            author=self.user)

        response1 = self.guest_client.get(reverse('index'))

        self.assertEqual(response0.content, response1.content,
                         'Ошибка кеширования.')

        cache.clear()
        response2 = self.guest_client.get(reverse('index'))

        self.assertNotEqual(response1.content, response2.content,
                            'Ошибка кеширования.')
