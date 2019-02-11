# -*- coding: utf-8 -*-

import unittest

from mailem import Attachment, ImageAttachment
from mailem.template import Template, TemplateRegistry
from mailem.template.renderer import Jinja2TemplateRenderer

from future.utils import PY2


class TemplateTest(unittest.TestCase):
    def _check_signup_template(self, signup):
        msg = signup(['kolypto@gmail.com'], dict(user='Honored User'), attachments=[
            Attachment('kolypto.gpg', '123'),
        ])

        # Accessing protected fields is discouraged, but still, let's make sure they're alright
        self.assertEqual(msg._subject, u'Hello Honored User °C')
        self.assertEqual(msg._html,
                         u'You are signed up -- <img src="cid:flower.jpg" /> localhost\n')
        self.assertEqual(msg._text, None)
        self.assertEqual(msg._sender, None)
        self.assertEqual(msg._cc, [])
        self.assertEqual(msg._bcc, [])
        self.assertEqual(msg._reply_to, None)

        # MIME message
        msg_str = str(msg)

        self.assertIn('Subject: =?utf-8?q?Hello_Honored_User_=C2=B0C?=', msg_str)
        self.assertIn('To: kolypto@gmail.com', msg_str)
        self.assertIn('You are signed up -- <img src="cid:flower.jpg" /> localhost', msg_str)

        if PY2:
            self.assertIn('Content-Disposition: inline; filename="=?utf-8?q?flower=2Ejpg?="', msg_str)
        else:
            self.assertIn('Content-Disposition: inline; filename="flower.jpg"', msg_str)
        #self.assertIn('Content-Type: image/jpeg', msg_str)
        self.assertIn('Content-ID: <flower.jpg>', msg_str)

        if PY2:
            self.assertIn('Content-Disposition: attachment; filename="=?utf-8?q?kolypto=2Egpg?="', msg_str)
        else:
            self.assertIn('Content-Disposition: attachment; filename="kolypto.gpg"', msg_str)
        self.assertIn('Content-Type: application/octet-stream', msg_str)

    def test_template(self):
        """ Test Template """
        signup = Template(
            u'Hello $user °C',
            'You are signed up -- <img src="cid:flower.jpg" /> $domain\n',
            attachments=[
                ImageAttachment('flower.jpg', b'\xff\xd8\xff\xe0\x00\x10JFIF', 'inline'),
            ],
            defaults=dict(domain='localhost')
        )
        self._check_signup_template(signup)

    def test_jinja2(self):
        """ Test jinja2 template renderer """
        signup = Template(
            u'Hello {{ user }} °C',
            'You are signed up -- <img src="cid:flower.jpg" /> {{ domain }}\n',
            attachments=[
                ImageAttachment('flower.jpg', b'\xff\xd8\xff\xe0\x00\x10JFIF', 'inline'),
            ],
            defaults=dict(domain='localhost')
        )
        signup.set_renderer(Jinja2TemplateRenderer)
        self._check_signup_template(signup)

    def test_from_directory(self):
        """ Test Template.from_directory() """
        signup = Template.from_directory('tests/data/signup')
        signup.defaults(dict(domain='localhost'))
        self._check_signup_template(signup)

    def test_registry(self):
        """ Test TemplateRegistry """
        registry = TemplateRegistry.from_directory('tests/data').defaults(dict(domain='localhost'))
        self._check_signup_template(registry.get('signup'))
