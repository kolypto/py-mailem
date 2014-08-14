import unittest
import smtplib

from mailem import Message, Postman
from mailem.connection import SMTPConnection


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
            self.assertIn('Username and Password not accepted', e.smtp_error)
