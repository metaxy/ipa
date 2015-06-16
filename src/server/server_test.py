
import time
from os.path import join, dirname, realpath
from unittest import TestCase, main
from tempfile import NamedTemporaryFile, TemporaryDirectory
from subprocess import *
import requests as rq
import atexit

port = 5124

class ApiTest(TestCase):
    def setUp(self):
        # create database directory
        self.tmpdir = TemporaryDirectory()
        script = join(dirname(realpath(__file__)), 'server.py')
        testdb = join(self.tmpdir.name, 'test.db')
        
        check_call(['python3', script, '--debug', '--database', testdb, '--create-db'],
                stdout=DEVNULL, stderr=DEVNULL,
                cwd=self.tmpdir.name)

        global port
        self.url = 'http://localhost:'+str(port)+'/api/'
        self.server = Popen(['python3', script, '--debug', '--database', testdb, '--port', str(port)],
                stdout=DEVNULL, stderr=DEVNULL,
                cwd=self.tmpdir.name)

        def kill():
            if self.server.poll() is None:
                self.server.kill()
                self.server.wait()
        atexit.register(kill)

        port += 1
        time.sleep(1) # wait for server to start up

    def tearDown(self):
        self.server.kill()
        self.server.wait()
        # the temporary files will be removed automatically


    def login(self, uid='test1'):
        r = rq.post(self.url+'login', json={'uid': uid, 'password': uid})
        self.ok(r)
        return r.cookies

    def success(self, r):
        self.assertEqual(r.status_code, 200)

    def ok(self, r):
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['result'], 'ok')
    
    def denied(self, r):
        self.assertEqual(r.status_code, 403)

    def conflict(self, r):
        self.assertEqual(r.status_code, 409)

    def bad(self, r):
        self.assertEqual(r.status_code, 400)

    def notfound(self, r):
        self.assertEqual(r.status_code, 404)


    def testLogin(self):
        self.denied (rq.post(self.url+'login', json={'uid': 'test1', 'password': 'invalid password'}))
        self.denied (rq.post(self.url+'login', json={'uid': 'test1', 'password': ''}))
        self.denied (rq.post(self.url+'login', json={'uid': '', 'password': 'invalid password'}))
        self.ok     (rq.post(self.url+'login', json={'uid': 'test1', 'password': 'test1'}))

    def testCreateRoom(self):
        cred = self.login('user1')
        self.denied     (rq.post(self.url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))

        cred = self.login('lecturer1')
        self.success    (rq.post(self.url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))
        self.success    (rq.post(self.url+'create_room', json={'name': 'ünicödeが好き！', 'passkey': 'testpass1'}, cookies=cred))
        self.conflict   (rq.post(self.url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))

    def testAccessRoom(self):
        cred = self.login('user1')
        self.notfound(rq.get (self.url+'r/a_room_that_does_not_exist', cookies=cred))

        r = rq.get(self.url+'r/test_room_access', cookies=cred)
        self.success(r)
        j = r.json()
        for key in ('name', 'questions', 'surveys', 'user_is_lecturer'):
            self.assertIn(key, j)
        self.assertEqual(j['name'], 'test_room_access')
        self.assertIs(list, type(j['surveys']))
        self.assertEqual(1, len(j['surveys']))
        self.assertIs(list, type(j['questions']))
        self.assertEqual(1, len(j['questions']))
        self.assertEqual(False, j['user_is_lecturer'])

        self.denied (rq.get (self.url+'r/test_room_deny', cookies=cred))
        self.ok     (rq.post(self.url+'r/test_room_deny/enter', json={'passkey': 'test_passkey'}, cookies=cred))
        self.success(rq.get (self.url+'r/test_room_deny', cookies=cred))

        cred = self.login('lecturer1')
        r = rq.get(self.url+'r/test_room_access', cookies=cred)
        self.success(r)
        j = r.json()
        self.assertEqual(True, j['user_is_lecturer'])

    def testCreateSurvey(self):
        cred = self.login('user1')
        testsv = {'title': 'test 1', 'options': ['opt1', 'opt2', 'really long opt'*100]}
        self.denied (rq.post(self.url+'r/test_room_access/create_survey', json=testsv, cookies=cred))

        cred = self.login('lecturer1')
        testsv = {'title': 'test 2', 'options': []}
        self.bad    (rq.post(self.url+'r/test_room_access/create_survey', json=testsv, cookies=cred))
        testsv = {'title': 'test 3', 'options': ['opt1']}
        self.bad    (rq.post(self.url+'r/test_room_access/create_survey', json=testsv, cookies=cred))
        testsv = {'title': 'test 5', 'options': ['opt1', 'opt2', 'opt3', 'opt4']}
        self.ok     (rq.post(self.url+'r/test_room_access/create_survey', json=testsv, cookies=cred))
        testsv = {'title': 'test 4', 'options': ['opt1', 'opt2', 'opt3', 'opt4', 'opt5']}
        self.bad    (rq.post(self.url+'r/test_room_access/create_survey', json=testsv, cookies=cred))

    def testCloseSurvey(self):
        cred = self.login('user1')
        r = rq.get(self.url+'r/test_room_access', cookies=cred)
        self.success(r)
        sid = r.json()['surveys'][0]['id']

        self.denied  (rq.post(self.url+'r/test_room_access/s/'+str(sid)+'/close', cookies=cred))

        cred = self.login('lecturer1')
        self.ok      (rq.post(self.url+'r/test_room_access/s/'+str(sid)+'/close', cookies=cred))
        self.notfound(rq.post(self.url+'r/test_room_access/s/123456789/close', cookies=cred))

    def testCreateQuestion(self):
        cred = self.login('user2')
        self.denied(rq.post(self.url+'r/test_room_access/create_question', json={'text': 'test 1'}, cookies=cred))
        
        cred = self.login('user1')
        self.ok      (rq.post(self.url+'r/test_room_access/create_question', json={'text': 'test 2'}, cookies=cred))
        self.notfound(rq.post(self.url+'r/unknown_room/create_question', json={'text': 'test 3'}, cookies=cred))

        cred = self.login('lecturer1')
        self.ok(rq.post(self.url+'r/test_room_access/create_question', json={'text': 'test 4'}, cookies=cred))

    def testDeleteQuestion(self):
        cred = self.login('user1')
        r = rq.get(self.url+'r/test_room_access', cookies=cred)
        self.success(r)
        qid = r.json()['questions'][0]['id']

        self.denied  (rq.post(self.url+'r/test_room_access/q/'+str(qid)+'/delete', cookies=cred))

        cred = self.login('lecturer1')
        self.ok      (rq.post(self.url+'r/test_room_access/q/'+str(qid)+'/delete', cookies=cred))
        self.notfound(rq.post(self.url+'r/test_room_access/q/123456789/delete', cookies=cred))


if __name__ == '__main__':
    main()

