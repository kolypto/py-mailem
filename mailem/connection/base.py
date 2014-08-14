class IConnection(object):
    """ Interface for connection objects """

    def connect(self):
        """ Establish a connection """
        raise NotImplementedError()

    def disconnect(self):
        """ Terminate the connection """
        raise NotImplementedError()

    def sendmail(self, message):
        """ Send the message

        :type msg: Message
        """
        raise NotImplementedError()
