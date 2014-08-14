"""
Full-featured e-mailing system: flexible, slim and sexy.

* Unicode
* Easy attachments
* Inline images
* E-Mail templates
* Tools for unit-tests
"""

from .message import Message
from .attachment import Attachment
from .postman import Postman
from . import connection
