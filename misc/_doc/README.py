import mailem
from exdoc import doc, getmembers

import json

data = {
    'mailem': doc(mailem),
    'Message': doc(mailem.Message),
    'Attachment': doc(mailem.Attachment),
    'ImageAttachment': doc(mailem.ImageAttachment),
    'Postman': {
        'cls': doc(mailem.Postman),
        'attrs': {name: doc(m) for name, m in getmembers(mailem.Postman)}
    },
    'connection': doc(mailem.connection),
    'SMTPConnection': doc(mailem.connection.SMTPConnection),
    'LoopbackConnection': doc(mailem.connection.LoopbackConnection),
}

print json.dumps(data, indent=2)
