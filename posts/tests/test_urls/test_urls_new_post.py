from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class PostsURLTests(TestCase):
    AUTH_USER = 'testname1'
    GROUP_TITLE = 'Тестовое название группы'
    GROUP_SLUG = 'test-slug'
    GROUP_DSCRPTN = 'Тестовое описание группы'
    POST_TEXT = 'Тестовый текст поста'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(
            username=cls.AUTH_USER)
        # Создадим запись в БД для проверки доступности адреса group/test-slug/
        cls.group = Group.objects.create(title=cls.GROUP_TITLE,
                                         slug=cls.GROUP_SLUG,
                                         description=cls.GROUP_DSCRPTN,
                                         )

        cls.post = Post.objects.create(text=cls.POST_TEXT,
                                       author=cls.user,
                                       group=cls.group,
                                       )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.reverse_name_new_post = reverse('new_post')

    # Проверяем редиректы для неавторизованного пользователя
    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(self.reverse_name_new_post, follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')
