from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class PostsURLTests(TestCase):
    USER_AUTHOR = 'testname1'
    AUTH_USER = 'testname2'
    GROUP_TITLE = 'Тестовое название группы'
    GROUP_SLUG = 'test-slug'
    GROUP_DSCRPTN = 'Тестовое описание группы'
    POST_TEXT = 'Тестовый текст поста'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = get_user_model().objects.create(
            username=cls.USER_AUTHOR)

        cls.user = get_user_model().objects.create(
            username=cls.AUTH_USER)

        cls.group = Group.objects.create(title=cls.GROUP_TITLE,
                                         slug=cls.GROUP_SLUG,
                                         description=cls.GROUP_DSCRPTN,
                                         )

        cls.post = Post.objects.create(text=cls.POST_TEXT,
                                       author=cls.user_author,
                                       group=cls.group,
                                       )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user_author)

        self.reverse_name_post = reverse('post',
                                         kwargs={'username': self.USER_AUTHOR,
                                                 'post_id': self.post.pk})
        self.reverse_name_post_edit = reverse('post_edit',
                                              kwargs={
                                                  'username': self.USER_AUTHOR,
                                                  'post_id': self.post.pk})

    def test_post_edit_url_guest_client(self):
        """URL редактирования поста для неавторизованного клиента"""
        response = self.guest_client.get(self.reverse_name_post_edit,
                                         follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/{self.USER_AUTHOR}/'
                      f'{self.post.pk}/edit/')

    def test_post_edit_url_authorized_client(self):
        """URL редактирования поста для авторизованного не автора поста"""
        response = self.authorized_client.get(self.reverse_name_post_edit,
                                              follow=True)
        self.assertRedirects(
            response, self.reverse_name_post)
