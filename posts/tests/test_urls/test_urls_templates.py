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

        self.templates_url_names = {
            '/index.html': self.reverse_name_index,
            '/group.html': self.reverse_name_group,
            'posts/new.html': self.reverse_name_new_post,
            'posts/profile.html': self.reverse_name_profile,
            'posts/post.html': self.reverse_name_post,
            'posts/post_edit.html': self.reverse_name_post_edit,
        }

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, url in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
