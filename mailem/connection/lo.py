from .base import IConnection


class LoopbackConnection(list, IConnection):
    """ Loopback connection allows to record all outgoing messages instead of sending them.

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
    """

    def __init__(self):
        super(LoopbackConnection, self).__init__()

    def connect(self):
        pass

    def disconnect(self):
        pass

    def sendmail(self, message):
        self.append(message)

    #region Access messages

    def get_messages(self):
        """ Get all messages and reset the internal queue

        :return: List of recorded messages
        :rtype: list[mailem.Message]
        """
        return [self.pop() for i in range(len(self))]

    #endregion
