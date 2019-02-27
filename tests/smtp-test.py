# -*- coding: utf-8 -*-

import unittest
import smtplib
from time import sleep

from mailem import Message, Postman
from mailem.connection import SMTPConnection

try:
    import aiosmtpd

    from aiosmtpd.controller import Controller
    from .asyncio_utils import StashingHandler
except ImportError:
    aiosmtpd = None


class TestSMTP(unittest.TestCase):
    def test_smtp(self):
        # Fake
        msg = Message(['test@gmail.com'], 'Test')
        postman = Postman('test@example.com',
                          SMTPConnection(
                              'smtp.gmail.com', 587,
                              'test@gmail.com', 'wrong',
                              tls=True))

        # try to connect: an error should occur
        try:
            with postman.connect() as c:
                raise AssertionError('Exception not raised')
        except smtplib.SMTPAuthenticationError as e:
            self.assertEqual(e.smtp_code, 535)
            self.assertIn(b'Username and Password not accepted', e.smtp_error)

    def test_real_mail_smtp(self):
        """ Test sending messages with a real-world SMTPD server """
        if aiosmtpd is None:
            self.skipTest('aiosmtpd not available')

        aiosmtpd_port = 50587

        # Start an smtp server
        mail_handler = StashingHandler()
        controller = Controller(mail_handler, loop=None,
                                hostname='localhost', port=aiosmtpd_port)
        controller.start()

        # Give it time to settle
        sleep(0.5)

        # Initialize a Postman
        postman = Postman('test@example.com',
                          NoLoginSMTP('localhost', aiosmtpd_port, None, None))

        # Send messages
        with postman.connect() as c:
            # Send plaintext message
            msg = Message(['test@example.com'], 'Subject', 'HTML message')
            c.sendmail(msg)

            # Send unicode message
            msg = Message(['test@example.com'], u'Håkon', u'Håkon')
            c.sendmail(msg)

        # Done
        controller.stop()

        # Test
        self.assertEqual(len(mail_handler.mail), 2)


class NoLoginSMTP(SMTPConnection):
    # aiosmtpd does not support AUTH: we can't login()
    # Thus, override it with a method that connects without authentication
    def connect(self):
        self.client = self._get_client()
