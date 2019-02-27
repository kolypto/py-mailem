# Used in smtp-test: mail handler
# Moved here because `async def` is a syntax error in < 3.7

class StashingHandler(object):
    def __init__(self):
        self.mail = []

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not address.endswith('@example.com'):
            return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        self.mail.append(
            (envelope.mail_from, envelope.content.decode('utf8', errors='replace'))
        )
        return '250 Message accepted for delivery'
