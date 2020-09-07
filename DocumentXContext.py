import requests
import hashlib
import json
import getpass

class DocumentXContext():
    def __init__(self, endpoint='https://apis.mcsrv.icu'):
        self.uID = None
        self.token = None
        self.name = None
        self.endpoint = endpoint
        super().__init__()

    class ServerSideException(Exception):
        'Server side exception'
        pass

    def login(self, uID: str, password: str):
        r = self.post('/login', {
            'uID': uID,
            'password': hashlib.md5(password.encode()).hexdigest()
        }, use_cridentials=False)
        if r:
            self.uID = r['uID']
            self.name = r['name']
            self.token = r['token']
            return self
        else:
            raise Exception('Login Failed.')

    def get(self, route, params={}, *args, json=True, use_cridentials=True, **kw):
        if use_cridentials:
            params['uID'] = self.uID
            params['token'] = self.token

        r = requests.get(self.endpoint+route, params=params, **kw)
        if json:
            try:
                res = r.json()
                if res['code'] != 0:
                    raise self.ServerSideException(
                        'Server Side Exception ('+str(res['code'])+'): '+str(res['message']))
                return res
            except self.ServerSideException:
                raise
            except Exception as e:
                print(e)
                return {}
        else:
            return r

    def post(self, route, data={}, *args, json=True, use_cridentials=True, **kw):
        if use_cridentials:
            params['uID'] = self.uID
            params['token'] = self.token

        r = requests.post(self.endpoint+route, data=data, **kw)
        if json:
            try:
                res = r.json()
                if res['code'] != 0:
                    raise self.ServerSideException(
                        'Server Side Exception ('+str(res['code'])+'): '+str(res['message']))
                return res
            except self.ServerSideException:
                raise
            except Exception as e:
                print(e)
                return {}
        else:
            return r

    def getAllDocuments(self, status='all', limit=[0, 0]):
        'Valid status: all / active / archived'
        res = self.get('/getDocuments', {
            'status': status,
            'start': limit[0],
            'end': limit[1]
        })
        if res:
            return res['result']

    def searchDocumentsByHashTag(self, hashTag='', limit=[0, 0]):
        res = self.get('/searchDocumentsByHashTag', {
            'hashTag': hashTag,
            'start': limit[0],
            'end': limit[1]
        })
        if res:
            return res['result']

    def share(self, docID, targetUID, read=True, write=False):
        res = self.get('/share', {
            'targetUID': targetUID,
            'read': str(read).lower(),
            'write': str(write).lower(),
            'docID': docID
        })
        if res:
            return res['code']

    def deleteDocumentByID(self, docID):
        res = self.get('/deleteDocumentByID', {
            'docID': docID
        })
        if res:
            return res['code']

    def editDocumentByID(self, docID, properties):
        res = self.get('/editDocumentByID', {
            'docID': docID,
            'properties': json.dumps(properties)
        })
        if res:
            return res['success'], res['failed']

    def getDocumentByID(self, docID):
        res = self.get('/getDocumentByID', {
            'docID': docID
        })
        if res:
            return res['result']

    def getDownloadLink(self, docID):
        res = self.get('/getDownloadLink', {
            'docID': docID
        })
        if res:
            return self.endpoint+res['link']

    def Document(self, docID):
        return self._Document(self, docID)

    class _Document():
        def __init__(self, ctx, docID):
            self.ctx = ctx
            self.docID = docID
            self.name = None
            self.subject = None
            ctxres = ctx.getDocumentByID(docID)
            if ctxres:
                self.name = ctxres['name']
                self.subject = ctxres['subject']
            super().__init__()

        def share(self, targetUID, read=True, write=False):
            return self.ctx.share(self.docID, targetUID, read=read, write=write)

        def delete(self):
            return self.ctx.deleteDocumentByID(self.docID)

        def edit(self, properties):
            return self.ctx.editDocumentByID(self.docID, properties)

        def getInfo(self):
            return self.ctx.getDocumentByID(self.docID)

        def getLink(self):
            return self.ctx.getDownloadLink(self.docID)