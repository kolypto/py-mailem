""" Helpers & Utils """

from email import charset
from email.header import Header
from email.utils import formataddr


# Add charset to the global registry, since we're only using unicode here
# NOTE: global effect!
charset.add_charset('utf-8', charset.SHORTEST, None, 'utf-8')


def unicode_header(*args, **kwargs):
    """ Shortcut to create a unicode Header() string.

    :rtype: str
    """
    return str(Header(*args, charset='utf-8', **kwargs))


class Address(object):
    """ E-Mail address

    :param arg: e-mail address, or a 2-tuple (email, name)
    :type arg: basestring|tuple[basestring]
    """

    def __init__(self, arg):
        if isinstance(arg, basestring):
            self.email = arg
            self.name = None
        elif isinstance(arg, tuple) and len(arg) == 2:
            self.email, self.name = arg
        else:
            raise ValueError('Invalid address: should be a string or a 2-tuple, having: {!r}'.format(arg))

    def __hash__(self):
        return hash((self.email, self.name))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.email, self.name) == (other.email, other.name)

    def __str__(self):
        return formataddr((
            unicode_header(self.name) if self.name else None,
            self.email
        ))

    def __repr__(self):
        if not self.name:
            return u'Address({!r})'.format(self.email)
        return u'Address(({!r}, {!r}))'.format(self.email, self.name)
