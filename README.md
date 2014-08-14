[![Build Status](https://api.travis-ci.org/kolypto/py-mailem.png?branch=master)](https://travis-ci.org/kolypto/py-mailem)





Mail'Em
=======

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



Table of Contents
=================



Message
=======
```python
Message(recipients, subject, html=None,
        text=None, sender=None, cc=None,
        bcc=None, attachments=None,
        reply_to=None, date=None, headers=None)
```

Construct a Message object.

Notes:

* Full unicode support, and Unicode is the default
* You can provide `html` or `text` contents. If both are specified -- the message will have an 'alternative' container,
  so the user will receive both HTML and plaintext. The client will choose which one to display.
* E-Mail addresses, such as `recipients` and `sender`, can be specified in one of the following formats:

    * `'user@example.com'`: Just an e-mail address
    * `('user@example.com', u'Honored User')`: email address with name

Arguments:

* `recipients`: List of recipients
* `subject`: Message subject
* `html`: Message body, HTML
* `text`: Message body, Text
* `sender`: Sender e-mail address. If not set explicitly, the default will be used on send
* `cc`: CC list
* `bcc`: BCC list
* `attachments`: List of attachments
* `reply_to`: Reply-to address
* `date`: Send date
* `headers`: Additional headers


Attachment
----------
```python
Attachment(filename, data,
           content_type='application/octet-stream',
           disposition='attachment', headers=None)
```

File attachment information.

This can be provided to the [`Message`](#message) object on construction.

* `filename`: Filename of attachment
* `data`: Taw file data
* `content_type`: File mimetype
* `disposition`: Content-Disposition: 'attachment', 'inline', ...
* `headers`: Additional headers for the attachment


ImageAttachment
---------------
```python
ImageAttachment(filename, data,
                disposition='attachment', headers=None)
```

Image attachment.

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

* `filename`: Image attachment filename. Will also become 'Content-ID' when inlined.
* `data`: The raw file data




Postman
=======
```python
Postman(sender, connection)
```

Postman is the object you use to send messages through a configured Connection object.

Example:

```python
from mailem import Message, Postman
from mailem.connection import SMTPConnection

# Construct the message
msg = Message(
    ['kolypto@gmail.com'],
    u"Mail'em test",
    u"<b>yeah baby, it works!</b>"
)

# Create the postman (see SMTPConnection)
postman = Postman('user@gmail.com',
                  SMTPConnection(...))

# Connect, and send the message
with postman.connect() as c:
    c.sendmail(msg)
```

* `sender`: Default sender: e-mail or (name, email).
    Is used for messages which do not specify the sender address explicitly.
* `connection`: Connection object to use. See below.


### Postman.connect()
Get connected Postman context manager.

### Postman.loopback()
Get a context manager which installs a LoopbackConnection on this postman.

This allows you to record outgoing messages by mocking a Postman.
See [`LoopbackConnection`](#loopbackconnection).

Connection
==========

Connection object represents a connection to a service which can send e-mail messages for us.

SMTPConnection
--------------
```python
SMTPConnection(host, port, username,
               password, local_hostname=None,
               ssl=False, tls=False)
```

SMTP connection.

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

* `host`: SMTP server hostname
* `port`: SMTP server port number.
* `username`: User name to authenticate with
* `password`: Password
* `local_hostname`: FQDN of the local host for the HELO/EHLO command. When `None`, is detected automatically.
* `ssl`: Use SSL protocol?
* `tls`: Use TLS handshake?


LoopbackConnection
------------------
```python
LoopbackConnection()
```

Loopback connection allows to record all outgoing messages instead of sending them.

You can install it manually:

```python
from mailem import Postman
from mailem.connection import LoopbackConnection

lo = LoopbackConnection()
postman = Postman('user@example.com', lo)
#... send
messages = lo.get_messages()
```

or you can mock an existing Postman with `loopback()` helper:

```python
from mailem import Postman
from mailem.connection import SMTPConnection

postman = Postman('user@example.com',
              SMTPConnection(...))

with postman.loopback() as lo:
    # Send
    with postman.connect() as c:  # mocked!
        c.sendmail(msg)

# Get
sent_messages = lo.get_messages()
```

Loopback can be installed multiple times, and only top-level loopback will catch the messages:

```python
with postman.loopback() as lo1:
    with postman.loopback() as lo2:
        with postman.connect() as c:
            c.sendmail(msg)

len(lo1)  #-> 0
len(lo2)  #-> 1
```

Also note that `LoopbackConnection` subclasses `list`, so all list methods, including iteration, is available.



Template
========
