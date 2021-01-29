import shutil
import tempfile

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class ContextPageViewTests(TestCase):
    AUTH_USER = 'TestName'
    GROUP_TITLE = 'Тестовое название группы'
    GROUP_SLUG = 'test-slug'
    GROUP_DSCRPTN = 'Тестовое описание группы'
    POST_TEXT = 'Тестовый текст поста'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.user = get_user_model().objects.create(
            username=cls.AUTH_USER)

        cls.group = Group.objects.create(title=cls.GROUP_TITLE,
                                         slug=cls.GROUP_SLUG,
                                         description=cls.GROUP_DSCRPTN,
                                         )

        cls.post = Post.objects.create(text=cls.POST_TEXT,
                                       author=cls.user,
                                       group=cls.group,
                                       image=cls.uploaded
                                       )

        cls.uploaded_name = f'posts/{cls.uploaded.name}'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_new_post_page(self):
        """Тестирование формы в new_post."""
        response = self.authorized_client.get(reverse('new_post'))

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected,
                                      'Ошибка в форме')

    def test_index_context_page(self):
        """Тестирование содержания context в index."""
        response = self.authorized_client.get(reverse('index'))

        context_index = {
            self.POST_TEXT: response.context['page'][0].text,
            self.AUTH_USER: response.context['page'][0].author.username,
            self.GROUP_TITLE: response.context['page'][0].group.title,
            self.uploaded_name: response.context['page'][0].image,
        }

        for expected, value in context_index.items():
            with self.subTest():
                self.assertEqual(value, expected,
                                 'Данные переданные в context'
                                 'ошибочны. Ошибка в index')

    def test_group_context_page(self):
        """Тестирование содержания context в group."""
        response = self.authorized_client.get(reverse(
            'group_posts',
            kwargs={'slug': self.GROUP_SLUG}))

        context_group = {
            self.POST_TEXT: response.context['page'][0].text,
            self.AUTH_USER: response.context['page'][0].author.username,
            self.GROUP_TITLE: response.context['page'][0].group.title,
            self.GROUP_SLUG: response.context['page'][0].group.slug,
            self.GROUP_DSCRPTN: response.context['page'][0].group.description,
            self.uploaded_name: response.context['page'][0].image,
        }

        for expected, value in context_group.items():
            with self.subTest():
                self.assertEqual(value, expected,
                                 'Данные переданные в context '
                                 'ошибочны. Ошибка в group')

    def test_edit_post_context_page(self):
        """Тестирование содержания context при редактировании поста."""

        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={
                'username': self.AUTH_USER,
                'post_id': self.post.pk}))

        context_edit_post = {
            self.POST_TEXT: response.context.get('post').text,
            self.GROUP_TITLE: response.context.get('post').group.title,
        }

        for expected, value in context_edit_post.items():
            with self.subTest():
                self.assertEqual(value, expected,
                                 'Данные переданные в context'
                                 'ошибочны. Ошибка при редактировании поста')

    def test_profile_context_page(self):
        """Тестирование содержания context в profile."""

        response = self.guest_client.get(reverse(
            'profile',
            kwargs={
                'username': self.AUTH_USER}))

        context_profile = {
            self.POST_TEXT: response.context['page'][0].text,
            self.GROUP_TITLE: response.context['page'][0].group.title,
            self.AUTH_USER: response.context['page'][0].author.username,
            self.uploaded_name: response.context['page'][0].image,
        }

        for expected, value in context_profile.items():
            with self.subTest():
                self.assertEqual(value, expected,
                                 'Данные переданные в context'
                                 'ошибочны. Ошибка в profile')

    def test_post_context_page(self):
        """Тестирование содержания context на странице поста."""

        response = self.guest_client.get(reverse(
            'post',
            kwargs={'username': self.AUTH_USER,
                    'post_id': self.post.pk}))

        context_post = {
            self.POST_TEXT: response.context.get('post').text,
            self.GROUP_TITLE: response.context.get('post').group.title,
            self.AUTH_USER: response.context.get('post').author.username,
            self.uploaded_name: response.context.get('post').image,
        }

        for expected, value in context_post.items():
            with self.subTest():
                self.assertEqual(value, expected,
                                 'Данные переданные в context'
                                 'ошибочны. Ошибка на странице поста')
