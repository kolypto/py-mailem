import unittest
import smtplib

from mailem import Message, Postman


class TestLoopback(unittest.TestCase):
    def test_smtp(self):
        # Fake
        msg = Message(['test@gmail.com'], 'Test')
        postman = Postman('test@example.com', None)  # It's never used anyway

        # Cannot use `None` as Connection
        self.assertRaises(AttributeError, postman.connect().__enter__)

        # Mock and test
        with postman.loopback() as lo:
            # Send
            with postman.connect() as c:
                c.sendmail(msg)

            # Check
            self.assertEqual(len(lo), 1)

        self.assertEqual(len(lo), 1)  # Still usable

        # Now fails again
        self.assertRaises(AttributeError, postman.connect().__enter__)
