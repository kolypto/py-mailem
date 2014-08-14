"""
Full-featured e-mailing system: flexible, slim and sexy.

* Unicode
* Easy attachments
* Inline images
* E-Mail templates
* Tools for unit-tests
* Made perfect once and for all. Simple and cute :)

Here'a a full example:

```python
from mailem import Message, Postman, Attachment, ImageAttachment
from mailem.connection import SMTPConnection

# Create the message
messages = [
    # Message with attachments
    Message(
        ['kolypto@gmail.com'],
        u"Mail'em test",
        u"<b>yeah baby, it works!</b>",
        attachments = [
            Attachment(u'test.txt', open('test.txt').read())
        ]
    ),
    # Message with inline images (!)
    Message(
        ['kolypto@gmail.com'],
        u"Mail'em test with inline images",
        u"Cute: <img src='cid:cute.jpg' />",  # cid:<filename>
        attachments = [
            ImageAttachment('cute.jpg', open('cute.jpg').read(), 'inline')
        ]
    ),
]

# Initialize a postman with SMTP connection to GMail
postman = Postman('user@gmail.com',
                  SMTPConnection(
                      'smtp.gmail.com', 587,
                      'user@gmail.com', 'pass',
                      tls=True
                  ))

# Send everything we have
with postman.connect() as c:
    map(c.sendmail, messages)
```

Also see [Template](#template).
"""

from .message import Message
from .attachment import Attachment, ImageAttachment
from .postman import Postman
from . import connection, template
