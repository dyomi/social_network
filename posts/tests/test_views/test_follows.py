from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post


class FollowUserViewTest(TestCase):
    FOLLOWER_USER = 'TestName0'
    FOLLOWING_USER = 'TestName1'
    POST_TEXT = 'Тестовый текст поста'

    def setUp(self):
        self.follower_user = get_user_model().objects.create(
            username=self.FOLLOWER_USER)
        self.following_user = get_user_model().objects.create(
            username=self.FOLLOWING_USER)

        Post.objects.create(text=self.POST_TEXT,
                            author=self.following_user
                            )

        Post.objects.create(text=f'{self.POST_TEXT} другого пользователя',
                            author=self.follower_user
                            )

        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.follower_user)

        self.auth_client_author = Client()
        self.auth_client_author.force_login(self.following_user)

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
            'profile_unfollow',
            kwargs={
                'username': self.following_user
            }))

        self.assertFalse(Follow.objects.filter(user=self.follower_user,
                                               author=self.following_user),
                         'Отписка от пользователя не работает'
                         )

    def test_post_added_to_follow(self):
        """Тестирование на правильность работы подписки на пользователя."""

        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={
                'username': self.following_user
            }))

        posts = Post.objects.filter(
            author__following__user=self.follower_user)

        response_follower = self.auth_client_follower.get(
            reverse('follow_index'))
        response_author = self.auth_client_author.get(
            reverse('follow_index'))

        self.assertIn(posts.get(),
                      response_follower.context['paginator'].object_list,
                      'Запись отсутствует на странице подписок пользователя'
                      )

        self.assertNotIn(posts.get(),
                         response_author.context['paginator'].object_list,
                         'Запись добавлена к неверному пользователю.'
                         )
