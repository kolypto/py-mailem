# -*- coding: utf-8 -*-

import socket
import unittest
import smtplib
import smtpd
import threading
import asyncore
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
        # Set socket timeout (because in some cases the test hangs for 120 seconds)
        socket.setdefaulttimeout(2.0)
        self.addCleanup(socket.setdefaulttimeout, None)

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

    smtpd_port = 50587

    def test_real_mail_aiosmtpd(self):
        """ Test sending messages with a real-world SMTPD server """
        if aiosmtpd is None:
            self.skipTest('aiosmtpd not available')

        # Start an smtp server
        mail_handler = StashingHandler()
        controller = Controller(mail_handler, loop=None,
                                hostname='localhost', port=self.smtpd_port)
        controller.start()

        # Give it time to settle
        sleep(0.5)

        # Initialize a Postman
        postman = Postman('test@example.com',
                          NoLoginSMTP('localhost', self.smtpd_port, None, None))

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

    # TODO: remove this test when Python 2 becomes obsolete
    def test_real_mail_smtpd(self):
        """ Test sending messages with a real SMTPD server """
        # port+1 because python can't let it go.. :) hack?
        smtp_server = TestingSMTPServer(port=self.smtpd_port+1)
        smtp_server.start()
        sleep(0.5)

        # Initialize a Postman
        postman = Postman('test@example.com',
                          NoLoginSMTP('localhost', self.smtpd_port+1, None, None))

        # Send messages
        with postman.connect() as c:
            # Send unicode message
            c.sendmail(Message(['test@example.com'], u'Håkon', u'Håkon'))

        # Test
        self.assertIsNotNone(smtp_server.received_data)

        # Clean-up
        smtp_server.close()
        smtp_server.join()


class NoLoginSMTP(SMTPConnection):
    # aiosmtpd does not support AUTH: we can't login()
    # Thus, override it with a method that connects without authentication
    def connect(self):
        return self._get_client()



class TestingSMTPServer(smtpd.SMTPServer, threading.Thread):
    """ smtpd lib server """

    def __init__(self, port=25):
        self.received_peer = None
        self.received_mailfrom = None
        self.received_rcpttos = None
        self.received_data = None

        smtpd.SMTPServer.__init__(
            self,
            ('localhost', port),
            ('localhost', port)
        )
        threading.Thread.__init__(self)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        self.received_peer = peer
        self.received_mailfrom = mailfrom
        self.received_rcpttos = rcpttos
        self.received_data = data

        self.close()  # causes asyncore loop to quit

    def run(self):
        try:
            asyncore.loop()
        except asyncore.ExitNow:
            pass
