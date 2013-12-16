# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from cosinnus_etherpad.models import Etherpad
from tests.view_tests.base import ViewTestCase


class EditTest(ViewTestCase):

    def setUp(self, *args, **kwargs):
        super(EditTest, self).setUp(*args, **kwargs)
        self.pad = Etherpad.objects.create(group=self.group, title='foopad')
        self.kwargs = { 'group': self.group.slug, 'slug': self.pad.slug }
        self.url = reverse('cosinnus:etherpad:pad-edit', kwargs=self.kwargs)


    def tearDown(self, *args, **kwargs):
        # be nice to remote server and delete pad also there
        self.pad.delete()
        super(EditTest, self).tearDown(*args, **kwargs)


    def test_edit_get_not_logged_in(self):
        """
        Should return 403 on GET if not logged in
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_edit_get_logged_in(self):
        """
        Should return 200 on GET and have pad title set to readonly in form
        when logged in
        """
        self.client.login(username=self.credential, password=self.credential)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # content should have pad title in form set to readonlyy
        # TODO: test less template HTML code here
        self.assertIn(
            '<input class="form-control" id="id_title" maxlength="255" name="title" placeholder="Title" readonly="True" required="" title="" type="text" value="%s" />' % self.pad.title,
            response.content)

    def test_edit_post_not_logged_in(self):
        """
        Should return 403 on POST if not logged in
        """
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


    def test_edit_post_logged_in(self):
        """
        Should return 302 to detail page on successful POST and have tag
        saved to pad
        """
        self.client.login(username=self.credential, password=self.credential)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        tag = 'foo'
        params = {
            'csrfmiddlewaretoken': response.cookies['csrftoken'].value,
            'title': self.pad.title,
            'tags': tag,
        }
        response = self.client.post(self.url, params)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse('cosinnus:etherpad:pad-detail', kwargs=self.kwargs),
            response.get('location'))
        num_tags = len(self.pad.tags.filter(name=tag))
        self.assertEqual(num_tags, 1)
