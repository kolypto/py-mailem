import mailem
from exdoc import doc, getmembers

import json

doccls = lambda cls, *predicates: {
    'cls': doc(cls),
    'attrs': {name: doc(m) for name, m in getmembers(cls, *predicates)}
}

data = {
    'mailem': doc(mailem),
    'Message': doc(mailem.Message),
    'Attachment': doc(mailem.Attachment),
    'ImageAttachment': doc(mailem.ImageAttachment),
    'Postman': doccls(mailem.Postman),
    'connection': doc(mailem.connection),
    'SMTPConnection': doc(mailem.connection.SMTPConnection),
    'LoopbackConnection': doc(mailem.connection.LoopbackConnection),
    'Template': doccls(mailem.template.Template, None, lambda k, v: k=='__call__' or not k.startswith('_')),
    'TemplateRegistry': doccls(mailem.template.TemplateRegistry),
}

print json.dumps(data, indent=2)
