from .connection.lo import LoopbackConnection


class Postman(object):
    """ Postman is the object you use to send messages through a configured Connection object.

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

    :param sender: Default sender: e-mail or (name, email).
        Is used for messages which do not specify the sender address explicitly.
    :type sender: basestring|tuple[basestring]
    :param connection: Connection object to use. See below.
    :type connection: mailem.connection.IConnection
    """

    def __init__(self, sender, connection):
        self._sender = sender
        self._connection = connection

    def connect(self):
        """ Get connected Postman context manager.

        :rtype: mailem.postman.ConnectedPostman
        """
        return ConnectedPostman(self._sender, self._connection)

    def loopback(self):
        """ Get a context manager which installs a LoopbackConnection on this postman.

        This allows you to record outgoing messages by mocking a Postman.
        See [`LoopbackConnection`](#loopbackconnection).

        :return: Context manager which loops back outgoing messages
        :rtype: MockedPostman
        """
        return MockedPostman(self)


class ConnectedPostman(Postman):
    def __init__(self, *args):
        super(ConnectedPostman, self).__init__(*args)

    def sendmail(self, message):
        """ Send the message

        :param message: Message
        :type message: mailem.message.Message
        :return: The same message
        :rtype: mailem.message.Message
        """
        message._sender_default(self._sender)
        self._connection.sendmail(message)
        return message

    def __enter__(self):
        """ Connect """
        self._connection.connect()
        self._connected = True
        return self

    def __exit__(self, *exc):
        """ Disconnect """
        self._connection.disconnect()
        self._connected = False


class MockedPostman(LoopbackConnection):
    """ Mocks Postman with a loopback

    :param postman: Postman to mock
    :type postman: mailem.postman.Postman
    """

    def __init__(self, postman):
        self._postman = postman
        self._connection_back = None
        super(MockedPostman, self).__init__()

    def __enter__(self):
        # Backup
        self._connection_back = self._postman._connection
        # Mock with self
        self._postman._connection = self
        return self

    def __exit__(self, *exc):
        # Restore backup
        self._postman._connection = self._connection_back
