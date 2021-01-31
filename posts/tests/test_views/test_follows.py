from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post


class FollowUserViewTest(TestCase):
    FOLLOWER_USER = 'TestName0'
    FOLLOWING_USER = 'TestName1'
    AUTH_USER = 'TestName'
    POST_TEXT = 'Тестовый текст поста'

    def setUp(self):
        self.follower_user = get_user_model().objects.create(
            username=self.FOLLOWER_USER)
        self.following_user = get_user_model().objects.create(
            username=self.FOLLOWING_USER)
        self.user = get_user_model().objects.create(
            username=self.AUTH_USER)

        self.post = Post.objects.create(text=self.POST_TEXT,
                                        author=self.following_user)

        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.follower_user)

        self.auth_client_author = Client()
        self.auth_client_author.force_login(self.following_user)

        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_authorized_user_follow_to_other_user(self):
        """Тестирование подписки на пользователей."""
        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={
                'username': self.following_user
            }))
        self.assertTrue(Follow.objects.filter(user=self.follower_user,
                                              author=self.following_user),
                        'Подписка на пользователя не рабоатет'
                        )

    def test_authorized_user_unfollow(self):
        """Тестирование отписывания от пользователей."""
        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={
                'username': self.following_user
            }))
        self.auth_client_follower.get(reverse(
            'profile_unfollow',
            kwargs={
                'username': self.following_user
            }))

        self.assertFalse(Follow.objects.filter(user=self.follower_user,
                                               author=self.following_user),
                         'Отписка от пользователя не работает'
                         )

    def test_post_added_to_follow(self):
        """Тестирование появления поста у пользователя
        подписанного на автора поста."""

        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={
                'username': self.following_user
            }))

        response_follower = self.auth_client_follower.get(
            reverse('follow_index'))
        self.assertIn(self.post,
                      response_follower.context['paginator'].object_list,
                      'Запись отсутствует на странице подписок пользователя'
                      )

    def test_post_not_added_not_to_follow(self):
        """Тестирование того, что пост не появляется у пользователя
        не подписанного на автора поста."""

        response_not_follower = self.auth_client.get(
            reverse('follow_index'))

        self.assertNotIn(
            self.post,
            response_not_follower.context['paginator'].object_list,
            'Запись добавлена к неверному пользователю.'
        )
