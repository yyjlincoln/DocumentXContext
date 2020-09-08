from DocumentXContext import DocumentXContext
import getpass

# Query all documents of a user
ctx = DocumentXContext().login(input('uID:'), getpass.getpass('Password:'))
recipient = input('Share to:')
for doc in ctx.getDocuments(status='all'):
    if doc['subject'].lower()=='physics':
        override = True
        for policy in doc['policies']:
            if policy['uID'] == recipient:

                print('Existing sharing policy: '+doc['name'])
                print('#'+str(doc['docID']))
                print(
                    f'''Read: {str(policy['read'])}, write: {str(policy['write'])}''')
                override = True if input(
                    'Override? [Y/N] (N) >').lower() == 'y' else False
                print('Overriding!' if override else 'Skipping!')
                break

        if override:
            # Share Document
            try:
                # Get Document Context
                dctx = ctx.Document(doc['docID'])
                # Share with specific user
                dctx.share(recipient, read=True, write=False)
                print('Shared #'+str(dctx.docID)+'\t'+str(dctx.name))
            except ctx.ServerSideException as e:
                print(e)
