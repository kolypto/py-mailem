import smtplib
import itertools

from . import IConnection


class SMTPConnection(IConnection):
    """ SMTP connection """

    def __init__(self, host, port, username, password, local_hostname=None, ssl=False, tls=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.local_hostname = local_hostname
        self.ssl = ssl
        self.tls = tls

        self.client = None

    def connect(self):
        # Init
        s = (smtplib.SMTP_SSL
             if self.ssl else
             smtplib.SMTP)(self.host, self.port, self.local_hostname)

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
            str(message)
        )
