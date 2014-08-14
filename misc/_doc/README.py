import mailem
from exdoc import doc, getmembers

import json

data = {
    'mailem': doc(mailem),
    'Message': doc(mailem.Message),
    'Attachment': doc(mailem.Attachment),
    'ImageAttachment': doc(mailem.ImageAttachment),
    'Postman': doc(mailem.Postman),
    'connection': doc(mailem.connection),
    'SMTPConnection': doc(mailem.connection.SMTPConnection),
}

print json.dumps(data, indent=2)
