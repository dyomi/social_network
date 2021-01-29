from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()


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

        cls.group = Group.objects.create(title=cls.GROUP_TITLE,
                                         slug=cls.GROUP_SLUG,
                                         description=cls.GROUP_DSCRPTN,
                                         )

        cls.post = Post.objects.create(text=cls.POST_TEXT,
                                       author=cls.user,
                                       group=cls.group,
                                       )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.reverse_name_index = reverse('index')
        self.reverse_name_group = reverse('group_posts',
                                          kwargs={'slug': self.GROUP_SLUG})
        self.reverse_name_new_post = reverse('new_post')
        self.reverse_name_profile = reverse('profile',
                                            kwargs={
                                                'username': self.AUTH_USER})
        self.reverse_name_post = reverse('post',
                                         kwargs={'username': self.AUTH_USER,
                                                 'post_id': self.post.pk})
        self.reverse_name_post_edit = reverse('post_edit',
                                              kwargs={
                                                  'username': self.AUTH_USER,
                                                  'post_id': self.post.pk})

        self.url_name_status_code = {
            self.reverse_name_index: 200,
            self.reverse_name_group: 200,
            self.reverse_name_new_post: 200,
            self.reverse_name_profile: 200,
            self.reverse_name_post: 200,
            self.reverse_name_post_edit: 200,
        }

    def test_urls_authorized_client(self):
        """URL-адреса доступны авторизованным пользователям."""
        for url_name, status_code in self.url_name_status_code.items():
            with self.subTest(url=url_name):
                response = self.authorized_client.get(url_name)
                self.assertTemplateUsed(status_code, response.status_code,
                                        f'Неправильная работа url:'
                                        f' {url_name} для авторизованного '
                                        f'пользователя. Код: {status_code}')
