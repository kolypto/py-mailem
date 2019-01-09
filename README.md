[![Build Status](https://api.travis-ci.org/kolypto/py-mailem.png?branch=master)](https://travis-ci.org/kolypto/py-mailem)
[![Pythons](https://img.shields.io/badge/python-2.7%20%7C%203.4%E2%80%933.7%20%7C%20pypy-blue.svg)](.travis.yml)







Mail'Em
=======

Slim, flexible, yet full-featured e-mailing library.

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

* <a href="#sending-messages">Sending Messages</a>
    * <a href="#message">Message</a>
        * <a href="#attachment">Attachment</a>
        * <a href="#imageattachment">ImageAttachment</a>
    * <a href="#postman">Postman</a>
        * <a href="#postmanconnect">Postman.connect</a>
        * <a href="#postmanloopback">Postman.loopback</a>
    * <a href="#connection">Connection</a>
        * <a href="#smtpconnection">SMTPConnection</a>
        * <a href="#loopbackconnection">LoopbackConnection</a>
* <a href="#templating">Templating</a>
    * <a href="#template">Template</a>
        * <a href="#templateset_renderer">Template.set_renderer</a>
        * <a href="#templatedefaults">Template.defaults</a>
        * <a href="#templatecall">Template.call</a>
        * <a href="#templatefrom_directory">Template.from_directory</a>
    * <a href="#templateregistry">TemplateRegistry</a>
        * <a href="#templateregistryadd">TemplateRegistry.add</a>
        * <a href="#templateregistryset_renderer">TemplateRegistry.set_renderer</a>
        * <a href="#templateregistrydefaults">TemplateRegistry.defaults</a>
        * <a href="#templateregistryget">TemplateRegistry.get</a>
        * <a href="#templateregistryfrom_directory">TemplateRegistry.from_directory</a> 

Sending Messages
================

Message
----------------------
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


### Attachment
```python
Attachment(filename, data,
           content_type='application/octet-stream',
           disposition='attachment', headers=None)
```

File attachment information.

This can be provided to the [`Message`](#message) object on construction.

* `filename`: Filename of attachment
* `data`: Raw file data
* `content_type`: File mimetype
* `disposition`: Content-Disposition: 'attachment', 'inline', ...
* `headers`: Additional headers for the attachment


### ImageAttachment
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
----------------------
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


### Postman.connect
```python
connect()
```

Get connected Postman context manager.


Returns: `mailem.postman.ConnectedPostman` 

### Postman.loopback
```python
loopback()
```

Get a context manager which installs a LoopbackConnection on this postman.

This allows you to record outgoing messages by mocking a Postman.
See [`LoopbackConnection`](#loopbackconnection).


Returns: `MockedPostman` Context manager which loops back outgoing messages

Connection
----------

Connection object represents a connection to a service which can send e-mail messages for us.

### SMTPConnection
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


### LoopbackConnection
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





Templating
==========

Template
--------
```python
Template(subject=None, html=None,
         text=None, attachments=None,
         defaults=None)
```

A templated e-mail.

By default, the Template uses Python's `Template` renderer, which allows simple PHP-style substitution,
but this can be overridden using set_renderer().

First, a template is defined:

```python
from mailem import Attachment
from mailem.template import Template

signup = Template('Congrats $user, you've signed up!',
    'Welcome to our website!<br><img src="cid:logo.jpg" /> -- $domain',
    attachments=[
        Attachment('logo.jpg', open('logo.jpg').read(), 'inline'))
    ],
    defaults={'domain': 'localhost'}  # default template values
)
```

Now, having the template, you render it to a [`Message`](#message) by calling it:

```python
message = signup(['user@gmail.com'], dict(user='Honored User',))
```

Ready for sending! :)

* `subject`: Message subject template
* `html`: HTML message template, if any
* `text`: Text message template, if any
* `attachments`: Attachments for the template. Most probably, inline elements.
* `defaults`: Default template values, if required. The user can override these later.


### Template.set_renderer
```python
set_renderer(Renderer, **kwargs)
```

Set renderer to be used with this template.

A Renderer is any class that can be constructed with a template string argument,
and called with template values dict to render it.

When no renderer was explicitly set, it defaults to PythonTemplateRenderer.

See [mailem/template/renderer.py](mailem/template/renderer.py): it's easy to implement renderers with custom behavior!

* `Renderer`: Renderer class.
* `**kwargs`: Additional arguments to renderer, if supported



### Template.defaults
```python
defaults(values)
```

Set default values.

New values will overwrite the previous.

* `values`: Default template values



### Template.__call__
```python
__call__(recipients, values, **kwargs)
```

Create a `Message` object using the template values.

* `recipients`: Message recipients list
* `values`: Dictionary with template values
* `**kwargs`: keyword arguments for the [`Message`](#message) constructor

Returns: `Message` The rendered `Message` object

### Template.from_directory
```python
from_directory(path,
               subject_name='subject.txt',
               html_name='index.htm',
               text_name='index.txt',
               inline_rex='^i-(.*)')
```

Convenience class method to import a directory as a template:

* `subject.txt` is the subject string template
* `index.htm` is the HTML template
* `index.txt` is the plaintext template
* All files matching the 'i-(*)' format are attached as 'inline', and hence can be referenced in the template:

    E.g. file 'i-flower.jpg' can be inlined as `<img src="cid:flower.jpg" />`.

* All other files are just attachments.

Example:

```python
signup = Template.from_directory('templates/signup/')
```

* `path`: Path to the directory
* `subject_name`: Subject template filename
* `html_name`: Html template filename
* `text_name`: Plaintext template filename
* `inline_rex`: Regular expression to match files that should be inlined.

    If the RegExp defines capture groups, group $1 will be used as the fact filename.

Returns: `Template` Template

TemplateRegistry
----------------

```python
TemplateRegistry()
```

E-Mail template registry.

Simply contains all your templates and allows to render these by name.
Useful if you have multiple templates in your app and want to have them prepared.

Initially, the registry is empty, and you add [`Template`](#template) objects one by one:

```python
from mailem.template import Template, TemplateRegistry

templates = TemplateRegistry()
templates.add('signup', Template(
            'Congrats $user, you've signed up!',
           'Welcome to our website!<br> -- $domain',
))
templates.defaults(dict(domain='example.com'))  # set defaults on all templates
```

Alternatively, you can use [`TemplateRegistry.from_directory()`](#templateregistryfrom_directory) to load templates
from filesystem.

Now, to render a template, you [`get()`](#templateregistryget) it by name:

```python
msg = templates.get('signup')(['user@gmail.com'], dict(user='Honored User',))
```



### TemplateRegistry.add
```python
add(name, template)
```

Register a template


* `template`: Template object

Returns: `mailem.template.Template` The added template (in case you want to set something on it)

### TemplateRegistry.set_renderer
```python
set_renderer(renderer, **kwargs)
```

Set renderer to be used with all templates.

Can be called both before adding templates and after.

* `renderer`: Renderer class to use
* `**kwargs`: Additional arguments for the renderer



### TemplateRegistry.defaults
```python
defaults(values)
```

Set default values on all templates.

New values will overwrite the previous.

Can be called both before adding templates and after.

* `values`: Default template values



### TemplateRegistry.get
```python
get(name)
```

Get a Template by name

* `name`: Template name

Returns: `mailem.template.Template` 

### TemplateRegistry.from_directory
```python
from_directory(path, **kwargs)
```

Convenience method to construct a template registry
with a directory where each template is in a subdirectory

* `path`: Path to templates
* `**kwargs`: Arguments to [Template.from_directory()](#templatefrom_directory), if required

Returns: `mailem.template.registry.TemplateRegistry` 
