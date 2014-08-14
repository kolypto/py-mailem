""" Attachments """

import itertools
from urllib import quote_plus

from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

from .util import unicode_header


class Attachment(object):
    """ File attachment information.

    This can be provided to the [`Message`](#message) object on construction.

    :param filename: Filename of attachment
    :type filename: str|unicode|None
    :param data: Taw file data
    :type data: str|None
    :param content_type: File mimetype
    :type content_type: str|None
    :param disposition: Content-Disposition: 'attachment', 'inline', ...
    :type disposition: str|None
    :param headers: Additional headers for the attachment
    :type headers: dict|None
    """

    def __init__(self, filename, data, content_type='application/octet-stream', disposition='attachment', headers=None):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition
        self.headers = headers or {}

        # Inlining
        if self.disposition == 'inline':
            self.headers.setdefault('Content-ID', '<{}>'.format(quote_plus(filename)))

    def _build_mime_object(self):
        """ Create a MIMe object

        :rtype: email.mime.base.MIMEBase
        """
        obj = MIMEBase(*self.content_type.split('/'))
        obj.set_payload(self.data)
        encode_base64(obj)
        return obj

    def _mime(self):
        """ Build a MIME object for the attachment

        :return: MIMEBase
        :rtype: email.mime.base.MIMEBase
        """
        obj = self._build_mime_object()

        # Content-Disposition
        obj.add_header('Content-Disposition', self.disposition, filename=unicode_header(self.filename))

        # Add headers
        for k, v in self.headers.items():
            obj[k] = v
        #itertools.starmap(obj.add_header, self.headers.items())  # does not work

        # Finish
        return obj


class ImageAttachment(Attachment):
    """ Image attachment.

    * It guesses the Content-Type from the data stream
    * Supports 'inline' images: images embedded in the email. Useful for templates.

        Once an 'inline' image is created, its filename is used for 'Content-ID', which allows to reference it in the HTML body:

        ```python
        from mailem import Message, Attachment, ImageAttachment

        msg = Message(
            ['test@example.com'],
            'Hello',
            '<img src="cid:flowers.jpg" />',  # Referenced with "cid:<filename>"
            attachments=[
                ImageAttachment('flowers.jpg', open('flowers.jpg').read(), 'inline')
            ]
        )
        ```

    Arguments:

    :param filename: Image attachment filename. Will also become 'Content-ID' when inlined.
    :type filename: str|unicode|None
    :param data: The raw file data
    :type data: str|None
    """

    def __init__(self, filename, data, disposition='attachment', headers=None):
        super(ImageAttachment, self).__init__(filename, data, None, disposition, headers)

    def _build_mime_object(self):
        return MIMEImage(self.data)
