import itertools

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from .util import Address, unicode_header


class Message(object):
    """ Construct a Message object.

    Notes:

    * Full unicode support, and Unicode is the default
    * You can provide `html` or `text` contents. If both are specified -- the message will have an 'alternative' container,
      so the user will receive both HTML and plaintext. The client will choose which one to display.
    * E-Mail addresses, such as `recipients` and `sender`, can be specified in one of the following formats:

        * `'user@example.com'`: Just an e-mail address
        * `('user@example.com', u'Honored User')`: email address with name

    Arguments:

    :param recipients: List of recipients
    :type recipients: Iterable[basestring|tuple[basestring]]
    :param subject: Message subject
    :type subject: basestring
    :param html: Message body, HTML
    :type html: basestring|None
    :param text: Message body, Text
    :type text: basestring|None
    :param sender: Sender e-mail address. If not set explicitly, the default will be used on send
    :type sender: basestring|tuple[basestring]|None
    :param cc: CC list
    :type cc: Iterable[basestring|tuple[basestring]]|None
    :param bcc: BCC list
    :type bcc: Iterable[basestring|tuple[basestring]]|None
    :param attachments: List of attachments
    :type attachments: Iterable[mailem.attachment.Attachment]
    :param reply_to: Reply-to address
    :type reply_to: basestring|tuple[basestring]|None
    :param date: Send date
    :type date: datetime|None
    :param headers: Additional headers
    :type headers: dict
    """

    def __init__(self, recipients, subject, html=None, text=None, sender=None, cc=None, bcc=None, attachments=None, reply_to=None, date=None, headers=None):
        self._recipients = [Address(r) for r in recipients]
        self._subject = subject
        self._html = html
        self._text = text
        self._sender = Address(sender) if sender else None
        self._cc =  [Address(c) for c in cc or ()]
        self._bcc = [Address(b) for b in bcc or ()]
        self._attachments = attachments or []
        self._reply_to = Address(reply_to) if reply_to else None
        self._date = date
        self._headers = headers or {}
        self._msgid = make_msgid()

    def _sender_default(self, sender):
        """ Set the default sender address

        :param sender: Sender address
        :type sender: basestring|tuple[basestring]
        """
        if not self._sender:
            self._sender = Address(sender)

    def _mime(self):
        """ Build a MIME object for this message

        :return:
        :rtype: email.mime.text.MIMEText|email.mime.multipart.MIMEMultipart
        """
        # Text object
        text = [ MIMEText(data, type,  'utf-8')
                 for data, type in (
                     (self._html, 'html'),
                     (self._text, 'plain'))
                 if data is not None]
        if len(text) == 1:
            msg = text[0]
        else:
            msg = MIMEMultipart('alternative')
            for t in text:
                msg.attach(t)

        # Attachments
        if self._attachments:
            _text_msg = msg
            msg = MIMEMultipart()
            msg.attach(_text_msg)
            for a in self._attachments:
                msg.attach(a._mime())

        # Fields
        msg['Subject'] = unicode_header(self._subject)  # special

        # Headers
        headers = dict(self._headers)
        headers['Date'] = formatdate(self._date)  # handles `None` correctly
        headers['Message-ID'] = self._msgid
        headers.update({  # Address lists
            key: ', '.join(map(str, addresses))
            for key, addresses in (
                ('To', self._recipients),
                ('Cc', self._cc),
                ('Bcc', self._bcc),
                # Not lists, but added here (DRY)
                ('From', (self._sender,) if self._sender else None),
                ('Reply-To', (self._reply_to,) if self._reply_to else None))
            if addresses
        })

        # Finish
        for k, v in headers.items():
            msg[k] = v
        #itertools.starmap(msg.add_header, headers.items())
        return msg

    def __str__(self):
        """ Build the MIME object and get a string """
        return self._mime().as_string()
