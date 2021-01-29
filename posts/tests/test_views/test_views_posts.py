from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class PostsViewTests(TestCase):
    AUTH_USER = 'TestName'
    GROUP_TITLE = 'Тестовое название группы'
    GROUP_SLUG = 'test-slug'
    GROUP_DSCRPTN = 'Тестовое описание группы'
    POST_TEXT = 'Тестовый текст поста'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(username=cls.AUTH_USER)

        Group.objects.create(title=f'{cls.GROUP_TITLE}1',
                             slug=f'{cls.GROUP_SLUG}1',
                             description=f'{cls.GROUP_DSCRPTN}1')

        cls.post = Post.objects.create(text=cls.POST_TEXT,
                                       author=cls.user,
                                       group=Group.objects.get(
                                           title=f'{cls.GROUP_TITLE}1')
                                       )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_added_in_index_page(self):
        """Тестирование наличия поста на главной странице сайта."""

        response = self.authorized_client.get(
            reverse('index'))
        post_id = response.context.get('page')[0].pk
        self.assertEqual(post_id, self.post.pk,
                         f'Созданный пост c pk={post_id} '
                         f'не был найден на странице index'
                         )

    def test_post_added_in_group_page(self):
        """Тестирование наличия поста присвоенного группе на странице группы."""
        post = Post.objects.first()
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': f'{self.GROUP_SLUG}1'}))
        self.assertEqual(post.text, response.context.get('page')[0].text,
                         f'Запись {post} в группе'
                         f'{self.GROUP_SLUG} не найдена'
                         )

    def test_post_added_in_correct_group(self):
        """Тестирование на правильность назначения групп для постов."""
        # Созданный тестовый пост не должен содержаться не в своей группе.
        # Обратимся к группе test-group1, не содержит ли он иные записи
        # возьмем первую запись
        group = Group.objects.first()
        # исключим группу
        posts_out_of_group = Post.objects.exclude(group=group)
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': f'{self.GROUP_SLUG}1'}))

        group_list_exclude_posts_set = set(posts_out_of_group)
        # получим все записи в object_list
        all_posts_of_group_page = response.context.get(
            'paginator').object_list
        # проверим полученные значения на пересечение
        self.assertTrue(
            group_list_exclude_posts_set.isdisjoint(
                all_posts_of_group_page))
