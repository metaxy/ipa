
import time
from os.path import join, dirname, realpath
from unittest import TestCase, main
from tempfile import NamedTemporaryFile
from functools import wraps
from contextlib import contextmanager
from subprocess import *
import requests as rq

import server

port = 5124
@contextmanager
def testserver():
    global port
    with NamedTemporaryFile() as dbfile:
        script = join(dirname(realpath(__file__)), 'server.py')
        testdb = dbfile.name
        
        check_call(['python3', script, '--debug', '--database', testdb, '--create-db'],
                stdout=DEVNULL, stderr=DEVNULL
        )

        url = 'http://localhost:'+str(port)+'/api/'
        server = Popen(['python3', script, '--debug', '--no-reload', '--database', testdb, '--port', str(port)],
                stdout=DEVNULL, stderr=DEVNULL,
        )

        port += 1
        time.sleep(1) # wait for server to start up
        try:
            yield url
        finally:
            server.terminate()
            server.wait()

test_endpoints = {}
def test_for(endpoint):
    def deco(f):
        test_endpoints[endpoint] = f
        return f
    return deco


class ApiTest(TestCase):
    def login(self, url, uid='test1'):
        r = rq.post(url+'login', json={'uid': uid, 'password': uid})
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


    @test_for('login')
    def testLogin(self):
        with testserver() as url:
            self.denied (rq.post(url+'login', json={'uid': 'test1', 'password': 'invalid password'}))
            self.denied (rq.post(url+'login', json={'uid': 'test1', 'password': ''}))
            self.denied (rq.post(url+'login', json={'uid': '', 'password': 'invalid password'}))
            self.ok     (rq.post(url+'login', json={'uid': 'test1', 'password': 'test1'}))

    @test_for('create_room')
    def testCreateRoom(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.denied     (rq.post(url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.success    (rq.post(url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))
            self.success    (rq.post(url+'create_room', json={'name': 'ünicödeが好き！', 'passkey': 'testpass1'}, cookies=cred))
            self.conflict   (rq.post(url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))

    @test_for('enter_room')
    def testAccessRoom(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.notfound(rq.get (url+'r/a_room_that_does_not_exist', cookies=cred))

            r = rq.get(url+'r/test_room_access', cookies=cred)
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

            self.denied (rq.get (url+'r/test_room_deny', cookies=cred))
            self.ok     (rq.post(url+'r/test_room_deny/enter', json={'passkey': 'test_passkey'}, cookies=cred))
            self.success(rq.get (url+'r/test_room_deny', cookies=cred))

            cred = self.login(url, 'lecturer1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            j = r.json()
            self.assertEqual(True, j['user_is_lecturer'])

    @test_for('create_survey')
    def testCreateSurvey(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            testsv = {'title': 'test 1', 'options': ['opt1', 'opt2', 'really long opt'*100]}
            self.denied (rq.post(url+'r/test_room_access/create_survey', json=testsv, cookies=cred))

            cred = self.login(url, 'lecturer1')
            testsv = {'title': 'test 2', 'options': []}
            self.bad    (rq.post(url+'r/test_room_access/create_survey', json=testsv, cookies=cred))
            testsv = {'title': 'test 3', 'options': ['opt']}
            # test for maximum option number
            self.bad    (rq.post(url+'r/test_room_access/create_survey', json=testsv, cookies=cred))
            testsv = {'title': 'test 5', 'options': ['opt']*32}
            self.ok     (rq.post(url+'r/test_room_access/create_survey', json=testsv, cookies=cred))
            testsv = {'title': 'test 4', 'options': ['opt']*33}
            self.bad    (rq.post(url+'r/test_room_access/create_survey', json=testsv, cookies=cred))

    @test_for('close_survey')
    def testCloseSurvey(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            sid = r.json()['surveys'][0]['id']

            self.denied  (rq.post(url+'r/test_room_access/s/'+str(sid)+'/close', cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.ok      (rq.post(url+'r/test_room_access/s/'+str(sid)+'/close', cookies=cred))
            self.notfound(rq.post(url+'r/test_room_access/s/123456789/close', cookies=cred))

    @test_for('create_question')
    def testCreateQuestion(self):
        with testserver() as url:
            cred = self.login(url, 'user2')
            self.denied(rq.post(url+'r/test_room_access/create_question', json={'text': 'test 1'}, cookies=cred))
            
            cred = self.login(url, 'user1')
            self.ok      (rq.post(url+'r/test_room_access/create_question', json={'text': 'test 2'}, cookies=cred))
            self.notfound(rq.post(url+'r/unknown_room/create_question', json={'text': 'test 3'}, cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.ok(rq.post(url+'r/test_room_access/create_question', json={'text': 'test 4'}, cookies=cred))

    @test_for('delete_question')
    def testDeleteQuestion(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            qid = r.json()['questions'][0]['id']

            self.denied  (rq.post(url+'r/test_room_access/q/'+str(qid)+'/delete', cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.ok      (rq.post(url+'r/test_room_access/q/'+str(qid)+'/delete', cookies=cred))
            self.notfound(rq.post(url+'r/test_room_access/q/123456789/delete', cookies=cred))
    
    def testUnitTestCoverage(self):
        with testserver() as url:
            """tests whether there is a unit test for every endpoint"""
            excluded_eps = {'static', 'view_index'}
            eps = {rule.endpoint for rule in server.app.url_map.iter_rules()} - excluded_eps
            self.assertSetEqual(eps, set(test_endpoints.keys()))


if __name__ == '__main__':
    main()

