import os
import re
from io import open

from .. import Message, Attachment
from .renderer import PythonTemplateRenderer


class Template(object):
    """ A templated e-mail.

    By default, the Template uses Python's `Template` renderer, which allows simple PHP-style substitution,
    but this can be overridden using set_renderer().

    First, a template is defined:

    ```python
    from mailem import Attachment
    from mailem.template import Template

    signup = Template('Congrats $user, you\'ve signed up!',
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

    :param subject: Message subject template
    :type subject: basestring|None
    :param html: HTML message template, if any
    :type html: basestring|None
    :param text: Text message template, if any
    :type text: basestring|None
    :param attachments: Attachments for the template. Most probably, inline elements.
    :type attachments: Iterable[mailem.Attachment]|None
    :param defaults: Default template values, if required. The user can override these later.
    :type defaults: dict|None
    """

    @classmethod
    def from_directory(cls, path, subject_name='subject.txt', html_name='index.htm', text_name='index.txt', inline_rex=r'^i-(.*)'):
        """ Convenience class method to import a directory as a template:

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

        :param path: Path to the directory
        :type path: str
        :param subject_name: Subject template filename
        :type subject_name: str
        :param html_name: Html template filename
        :type html_name: str
        :param text_name: Plaintext template filename
        :type text_name: str
        :param inline_rex: Regular expression to match files that should be inlined.

            If the RegExp defines capture groups, group $1 will be used as the fact filename.

        :returns: Template
        :rtype: Template
        """
        subject = None
        html = None
        text = None
        attachments = []

        text_file_names = (subject_name, html_name, text_name)

        # Find files
        for filename in os.listdir(path):
            # Ignore hidden files
            if filename.startswith('.'):
                continue
            fpath = os.path.join(path, filename)

            # Ignore directories
            if os.path.isdir(fpath):
                continue

            # Get content
            if filename in text_file_names:
                f = open(fpath, 'rt', encoding='utf-8')
            else:
                f = open(fpath, 'rb')
            with f:
                content = f.read()

            # Place
            if filename == subject_name:
                subject = content.strip()  # No \r\n allowed here
            elif filename == html_name:
                html = content
            elif filename == text_name:
                text = content
            else:
                # Match filename
                m = re.match(inline_rex, filename)
                if m is None:
                    # Attachment
                    disposition = 'attachment'
                else:
                    # Inline attachment
                    disposition = 'inline'
                    try:
                        # Has capture groups
                        filename = m.group(1)
                    except IndexError:
                        # Has no capture groups
                        filename = m.group(0)

                # Attach
                attachments.append(Attachment(filename, content, disposition=disposition))

        # Template
        return cls(subject=subject, html=html, text=text, attachments=attachments)

    def __init__(self, subject=None, html=None, text=None, attachments=None, defaults=None):
        self._subject = subject
        self._html = html
        self._text = text
        self._attachments = attachments
        self._default_values = {}
        self._renderer = None
        self.defaults(defaults or {})

    def defaults(self, values):
        """ Set default values.

        New values will overwrite the previous.

        :param values: Default template values
        :type values: dict
        """
        self._default_values.update(values)
        return self

    def set_renderer(self, Renderer, **kwargs):
        """ Set renderer to be used with this template.

        A Renderer is any class that can be constructed with a template string argument,
        and called with template values dict to render it.

        When no renderer was explicitly set, it defaults to PythonTemplateRenderer.

        See [mailem/template/renderer.py](mailem/template/renderer.py): it's easy to implement renderers with custom behavior!

        :param Renderer: Renderer class.
        :type Renderer: type
        :param kwargs: Additional arguments to renderer, if supported
        :type kwargs: dict
        """
        assert self._renderer is None, 'Cannot re-assign a renderer'

        self._renderer = Renderer
        self._subject = Renderer(self._subject, **kwargs)
        self._html = Renderer(self._html, **kwargs) if self._html else None
        self._text = Renderer(self._text, **kwargs) if self._text else None

        return self

    def __call__(self, recipients, values, **kwargs):
        """ Create a `Message` object using the template values.

        :param recipients: Message recipients list
        :type recipients: Iterable[basestring|tuple[basestring]]
        :param values: Dictionary with template values
        :type values: dict
        :param kwargs: keyword arguments for the [`Message`](#message) constructor
        :type kwargs: dict
        :returns: The rendered `Message` object
        :rtype: Message
        :raises KeyError: A template value was not provided
        :raises Exception: other renderer exceptions
        """
        # Default renderer
        if self._renderer is None:
            self.set_renderer(PythonTemplateRenderer)

        values = dict(list(self._default_values.items()) + list(values.items()))

        return Message(
            recipients,
            subject=self._subject(values),
            html=self._html(values) if self._html else None,
            text=self._text(values) if self._text else None,
            attachments=list(self._attachments or []) + list(kwargs.pop('attachments', [])),
            **kwargs
        )
