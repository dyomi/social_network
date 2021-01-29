from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class TemplateViewTests(TestCase):
    AUTH_USER = 'testname'
    GROUP_TITLE = 'Тестовое название группы'
    GROUP_SLUG = 'test-slug'
    GROUP_DSCRPTN = 'Тестовое описание группы'
    POST_TEXT = 'Тестовый текст поста'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(username=cls.AUTH_USER)

        Group.objects.create(title=cls.GROUP_TITLE,
                             slug=cls.GROUP_SLUG,
                             description=cls.GROUP_DSCRPTN,
                             )

        cls.post = Post.objects.create(text=cls.POST_TEXT,
                                       author=cls.user,
                                       group=Group.objects.get(
                                           title=cls.GROUP_TITLE)
                                       )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.reverse_name_index = reverse('index')
        self.reverse_name_group = reverse(
            'group_posts',
            kwargs={'slug': self.GROUP_SLUG})
        self.reverse_name_new_post = reverse('new_post')

        self.templates_page_names = {
            'index.html': self.reverse_name_index,
            'group.html': self.reverse_name_group,
            'posts/new.html': self.reverse_name_new_post,
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template,
                                        f'Проблема с шаблоном: {template}'
                                        f' reverse name: {reverse_name} '
                                        )
