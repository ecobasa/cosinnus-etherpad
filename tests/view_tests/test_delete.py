# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from cosinnus_etherpad.models import Etherpad
from tests.view_tests.base import ViewTestCase


class DeleteTest(ViewTestCase):

    def setUp(self, *args, **kwargs):
        super(DeleteTest, self).setUp(*args, **kwargs)
        self.pad = Etherpad.objects.create(group=self.group, title='testpad')
        self.kwargs = {'group': self.group.slug, 'slug': self.pad.slug}
        self.url = reverse('cosinnus:etherpad:pad-delete', kwargs=self.kwargs)

    def tearDown(self, *args, **kwargs):
        # be nice to remote server and delete pad also there
        if self.pad:  # only if not deleted already
            self.pad.delete()
        super(DeleteTest, self).tearDown(*args, **kwargs)

    def test_get_not_logged_in(self):
        """
        Should return 403 on GET if not logged in
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_logged_in(self):
        """
        Should return 200 on GET and have pad title set to readonly in form
        when logged in
        """
        self.client.login(username=self.credential, password=self.credential)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_not_logged_in(self):
        """
        Should return 403 on POST if not logged in
        """
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_logged_in(self):
        """
        Should return 302 to list page on successful POST and have pad deleted
        """
        self.client.login(username=self.credential, password=self.credential)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        params = {
            'csrfmiddlewaretoken': response.cookies['csrftoken'].value,
        }
        response = self.client.post(self.url, params)
        self.assertEqual(response.status_code, 302)
        kwargs = {'group': self.group.slug}
        self.assertIn(
            reverse('cosinnus:etherpad:list', kwargs=kwargs),
            response.get('location'))
        num_pads = len(Etherpad.objects.all())
        self.assertEqual(num_pads, 0)
        self.pad = None
