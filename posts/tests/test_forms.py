import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post


class NewPostFormTests(TestCase):
    # AUTH_USER = 'TestName'
    # GROUP_TITLE = 'Тестовое название группы'
    # GROUP_SLUG = 'test-slug'
    # GROUP_DSCRPTN = 'Тестовое описание группы'
    # POST_TEXT = 'Тестовый текст поста'

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

        # создаем авторизованного пользователя
        cls.user = get_user_model().objects.create(username='TestName')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post(self):
        """Тестирование формы создания поста."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
            'image': self.uploaded.name,
        }
        response = self.authorized_user.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с необходимым текстом
        self.assertTrue(Post.objects.filter(text='Тестовый текст').exists())


class PostEditFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='TestName')
        cls.group = Group.objects.create(title='Тестовое название группы',
                                         slug='test-slug',
                                         description='Тестовое описание')
        cls.post = Post.objects.create(text='Тестовый текст поста',
                                       author=cls.user,
                                       group=cls.group)

        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.form_data = {
            'text': 'Отредактированный тестовый текст поста',
            'group': cls.group.pk,
        }

    def test_forms_post_edit(self):
        """Тестирование формы редактирования постов."""

        response = self.authorized_user.post(
            reverse('post_edit',
                    kwargs={'username': 'TestName',
                            'post_id': self.post.pk}),
            data=self.form_data,
            follow=True)

        self.assertEqual(response.context['post'].text,
                         self.form_data['text'])


class AddCommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = get_user_model().objects.create(username='TestName')

        cls.post = Post.objects.create(text='Тестовый текст поста',
                                       author=cls.user,
                                       id='1')

    def test_user_cannot_add_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.guest_client.post(
            reverse(
                'add_comment',
                kwargs={'username': 'TestName', 'post_id': '1'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/TestName/1/comment'
        )
        self.assertEqual(Comment.objects.count(), comments_count)
