class Postman(object):
    """ Connection interface """

    def __init__(self, sender, connection):
        """ Init the connection with the default sender

        :param sender: Default sender: e-mail or (name, email)
        :type sender: basestring|tuple[basestring]
        :param connection: Connection to use
        :type connection: mailem.connection.IConnection
        """
        self._sender = sender
        self._connection = connection

    def connect(self):
        """ Get connected Postman context manager

        :rtype: mailem.postman.ConnectedPostman
        """
        return ConnectedPostman(self._sender, self._connection)


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
