# -*- coding: utf-8 -*-

import unittest

from mailem import Attachment, ImageAttachment
from mailem.template import Template


class TemplateTest(unittest.TestCase):
    def _check_signup_template(self, signup):
        msg = signup(['kolypto@gmail.com'], dict(user='Honored User'), attachments=[
            Attachment('kolypto.gpg', '123'),
        ])

        msg_str = str(msg)
        print msg_str

        self.assertIn('Subject: =?utf-8?q?Hello_Honored_User_=C2=B0C?=', msg_str)
        self.assertIn('To: kolypto@gmail.com', msg_str)
        self.assertIn('You are signed up -- <img src="cid:flower.jpg" /> localhost', msg_str)

        self.assertIn('Content-Disposition: inline; filename="=?utf-8?q?flower=2Ejpg?="', msg_str)
        #self.assertIn('Content-Type: image/jpeg', msg_str)
        self.assertIn('Content-ID: <flower.jpg>', msg_str)

        self.assertIn('Content-Disposition: attachment; filename="=?utf-8?q?kolypto=2Egpg?="', msg_str)
        self.assertIn('Content-Type: application/octet-stream', msg_str)

    def test_template(self):
        """ Test template """
        signup = Template(
            u'Hello $user °C',
            'You are signed up -- <img src="cid:flower.jpg" /> $domain',
            attachments=[
                ImageAttachment('flower.jpg', '\xff\xd8\xff\xe0\x00\x10JFIF', 'inline'),
            ],
            defaults=dict(domain='localhost')
        )
        self._check_signup_template(signup)

    def test_from_directory(self):
        signup = Template.from_directory('tests/data/signup')
        signup.defaults(dict(domain='localhost'))
        self._check_signup_template(signup)