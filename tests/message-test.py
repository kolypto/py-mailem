# -*- coding: utf-8 -*-

import unittest

from mailem import Message, Attachment, ImageAttachment

from future.utils import PY2


class MessageTest(unittest.TestCase):
    def test_html(self):
        msg = Message(
            ['kolypto@gmail.com'],
            u"Mail'em test °C",
            u"<b>yeah baby, it works!</b>",
            attachments=[
                Attachment(u'test.txt', 'abc')
            ],
            sender=('a@b', 'A'),
            cc=[('a@b', 'A'), 'b@b'],
            bcc=[('a@b', 'A'), 'b@b'],
            reply_to='z@b',
            headers={'Custom': 'Test'}
        )
        msg_str = str(msg)

        self.assertIn('multipart/mixed', msg_str)
        self.assertNotIn('multipart/alternative', msg_str)
        self.assertIn('text/html', msg_str)
        self.assertNotIn('text/plain', msg_str)

        self.assertIn('application/octet-stream', msg_str)
        self.assertIn('Content-Disposition: attachment; filename="test.txt"', msg_str)

        self.assertIn('Subject: =?utf-8?q?Mail=27em_test_=C2=B0C?=', msg_str)
        self.assertIn('To: kolypto@gmail.com', msg_str)
        if PY2:
            self.assertIn('From: =?utf-8?q?A?= <a@b>', msg_str)
            self.assertIn('Cc: =?utf-8?q?A?= <a@b>, b@b', msg_str)
            self.assertIn('Bcc: =?utf-8?q?A?= <a@b>, b@b', msg_str)
        else:
            self.assertIn('From: A <a@b>', msg_str)
            self.assertIn('Cc: A <a@b>, b@b', msg_str)
            self.assertIn('Bcc: A <a@b>, b@b', msg_str)
        self.assertIn('Reply-To: z@b', msg_str)
        self.assertIn('Message-ID:', msg_str)
        self.assertIn('Custom: Test', msg_str)
        self.assertIn('', msg_str)

    def test_html_text(self):
        msg = Message(
            ['kolypto@gmail.com'],
            u"Mail'em test",
            u'Mailtest',
            u"<b>yeah baby, it works!</b>",
            attachments=[
                Attachment(u'test.txt', 'abc')
            ]
        )
        msg_str = str(msg)

        self.assertIn('multipart/mixed', msg_str)
        self.assertIn('multipart/alternative', msg_str)
        self.assertIn('text/html', msg_str)
        self.assertIn('text/plain', msg_str)

        self.assertIn('Content-Type: application/octet-stream', msg_str)
        self.assertIn('Content-Disposition: attachment; filename="test.txt"', msg_str)

    def test_html_image(self):
        msg = Message(
            ['kolypto@gmail.com'],
            u"Mail'em test with inline images",
            u"Cute: <img src='cid:cute.jpg' />",  # cid:<filename>
            attachments=[
                ImageAttachment('cute.jpg', b'\xff\xd8\xff\xe0\x00\x10JFIF', 'inline')
            ]
        )
        msg_str = str(msg)

        self.assertIn('multipart/mixed', msg_str)
        self.assertNotIn('multipart/alternative', msg_str)
        self.assertIn('text/html', msg_str)
        self.assertNotIn('text/plain', msg_str)

        self.assertIn('Content-Type: image/jpeg', msg_str)
        self.assertIn('Content-ID: <cute.jpg>', msg_str)
        if PY2:
            self.assertIn('Content-Disposition: inline; filename="=?utf-8?q?cute=2Ejpg?="', msg_str)
        else:
            self.assertIn('Content-Disposition: inline; filename="cute.jpg"', msg_str)
