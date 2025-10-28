from django_webtest import WebTest
from django.urls import reverse


class ChatViewTest(WebTest):

    def test_can_get_chat_view_test(self):
        """If can reach the '/chat/ view"""
        response = self.app.get(reverse('chat:index'))

        self.assertEqual(200, response.status_code)

    def test_cant_reach_non_exisint_page(self):
        """If a page doesn't exist, it can't reach"""
        response = self.app.get('/test/', expect_errors=True)

        self.assertEqual(404, response.status_code)

    def test_can_go_to_chat_room(self):
        """User can go to a chat room"""
        response = self.app.get(reverse('chat:room', args=['test']))
        self.assertEqual(200, response.status_code)
