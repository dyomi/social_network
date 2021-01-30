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

        cache_len = str(response0.content)
        data_len = str(response1.content)

        self.assertEqual(cache_len, data_len,
                         'Количествозаписей переданных в context '
                         'не совпадает с количеством записей в базе. '
                         'Ошибка кеширования.')

        cache.clear()
        response2 = self.guest_client.get(reverse('index'))

        context_len = str(response2.content)

        self.assertNotEqual(data_len, context_len,
                            'Количествозаписей переданных в context '
                            'совпадает с количеством записей в базе. '
                            'Ошибка кеширования.')
