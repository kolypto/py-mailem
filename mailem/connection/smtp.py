import smtplib
import itertools

from .base import IConnection


class SMTPConnection(IConnection):
    """ SMTP connection.

    See [smtplib](https://docs.python.org/2/library/smtplib.html) for the list of exceptions that may occur.

    Example:

    ```python
    from mailem import Postman
    from mailem.connection import SMTPConnection

    postman = Postman('user@gmail.com',
                  SMTPConnection(
                      'smtp.gmail.com', 587,
                      'user@gmail.com', 'pass',
                      tls=True
                  ))

    with postman.connect() as c:
        c.sendmail(msg)
    ```

    Arguments:

    :param host: SMTP server hostname
    :type host: str
    :param port: SMTP server port number.
    :type port: int
    :param username: User name to authenticate with
    :type username: str
    :param password: Password
    :type password: str
    :param local_hostname: FQDN of the local host for the HELO/EHLO command. When `None`, is detected automatically.
    :type local_hostname: str|None
    :param ssl: Use SSL protocol?
    :type ssl: bool
    :param tls: Use TLS handshake?
    :type tls: bool
    """

    def __init__(self, host, port, username, password, local_hostname=None, ssl=False, tls=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.local_hostname = local_hostname
        self.ssl = ssl
        self.tls = tls

        self.client = None

    def _get_client(self):
        SMTP_CLS = smtplib.SMTP_SSL if self.ssl else smtplib.SMTP
        return SMTP_CLS(self.host, self.port, self.local_hostname)

    def connect(self):
        # Init
        s = self._get_client()

        # Handshake
        if self.tls:
            s.starttls()
        s.login(self.username, self.password)

        # Finish
        self.client = s

    def disconnect(self):
        self.client.quit()
        self.client = None

    def sendmail(self, message):
        self.client.sendmail(
            # From
            message._sender.email,

            # To
            [r.email for r in itertools.chain(
                message._recipients,
                message._cc,
                message._bcc)],

            # Message
            str(message).encode()
        )
