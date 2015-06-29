
import time
from os.path import join, dirname, realpath
from unittest import TestCase, main
from tempfile import NamedTemporaryFile
from functools import wraps
from contextlib import contextmanager
from subprocess import *
import requests as rq

import server

@contextmanager
def testserver():
    with NamedTemporaryFile() as dbfile:
        script = join(dirname(realpath(__file__)), 'server.py')
        testdb = dbfile.name
        
        check_call(['python3', script, '--debug', '--database', testdb, '--create-db'],
#                stdout=DEVNULL, stderr=DEVNULL
        )

        server = Popen(['python3', script, '--debug', '--no-reload', '--database', testdb, '--port', '5124'],
#                stdout=DEVNULL, stderr=DEVNULL,
        )

        time.sleep(1) # wait for server to start up
        try:
            yield 'http://localhost:5124/api/'
        finally:
            server.terminate()
            server.wait()

test_endpoints = {}
def test_for(endpoint):
    def deco(f):
        test_endpoints[endpoint] = f
        return f
    return deco


def sample_json(qv=0, sv=None):
    opts = ['opt1', 'opt2', 'opt3']
    if sv:
        foo = {'id': lambda x: True,
               'title': 'test survey',
               'options': opts,
               'results': set(zip(opts, sv)),
               'total': sum(sv)}
    else:
        foo = {'id': lambda x: True,
               'title': 'test survey',
               'options': opts}
    return {
        'name': 'test_room_access',
        'questions': [{
            'id': lambda x: True,
            'text': 'test question',
            'votes': qv
            }],
        'surveys': [foo],
        'user_is_lecturer': False
    }


class ApiTest(TestCase):
    def login(self, url, uid='test1'):
        r = rq.post(url+'login', json={'uid': uid, 'password': uid})
        self.ok(r)
        return r.cookies

    def status_code(self, r, status):
        self.assertEqual(r.status_code, status, r.request.url)

    def success(self, r):
        self.status_code(r, 200)

    def ok(self, r):
        self.status_code(r, 200)
        self.assertEqual(r.json()['result'], 'ok')
    
    def denied(self, r):
        self.status_code(r, 403)

    def conflict(self, r):
        self.status_code(r, 409)

    def bad(self, r):
        self.status_code(r, 400)

    def notfound(self, r):
        self.status_code(r, 404)

    def json_match(self, d, pat, _path='root'):
        if isinstance(pat, dict):
            for k,v in pat.items():
                self.assertIn(k, d)
                self.json_match(d[k], v, _path+'/'+k)
            self.json_match(len(d), len(pat))
        elif isinstance(pat, list):
            self.json_match(len(d), len(pat))
            for i,(a,b) in enumerate(zip(d, pat)):
                self.json_match(a, b, _path+'['+str(i)+']')
        elif isinstance(pat, set) and not isinstance(d, set):
            tupset = lambda v: set(v) if not isinstance(v, list) else {tuple(e) for e in v}
            self.json_match(tupset(d), pat)
        elif callable(pat):
            self.json_match(pat(d), True)
        else:
            try:
                self.assertEqual(d, pat)
            except AssertionError as e:
                e.args = (e.args[0]+'\nat path: '+_path,)
                raise e


    def testUnitTestCoverage(self):
        with testserver() as url:
            """tests whether there is a unit test for every endpoint"""
            excluded_eps = {'static', 'view_index'}
            eps = {rule.endpoint for rule in server.app.url_map.iter_rules()} - excluded_eps
            self.assertSetEqual(eps, set(test_endpoints.keys()))


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

    @test_for('list_rooms')
    def testListRooms(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'list_rooms', cookies=cred)
            self.success(r)
            self.assertSetEqual(set(r.json()['rooms']), {'test_room_access', 'test_room_deny'})

    @test_for('view_room')
    def testViewRoom(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            self.json_match(r.json(), sample_json())

    @test_for('vote_question')
    def testVoteQuestion(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            # Vote
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            qid = r.json()['questions'][0]['id']
            self.ok(rq.post(url+'r/test_room_access/q/'+str(qid)+'/vote', cookies=cred))
            # Check result
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            self.json_match(r.json(), sample_json(qv=1))
            # Vote again
            self.ok(rq.post(url+'r/test_room_access/q/'+str(qid)+'/vote', cookies=cred))
            # Check result again
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            self.json_match(r.json(), sample_json(qv=1))

    @test_for('vote_survey')
    @test_for('close_survey')
    def testVoteCloseSurvey(self):
        for i,j,votes in (
                ((0,),  (),     (1,0,0)),
                ((0,0), (),     (1,0,0)),
                ((0,),  (0,),   (2,0,0)),
                ((1,2), (1,),   (0,1,1)),
                ((2,),  (2,),   (0,0,2))):
            with testserver() as url:
                cred1 = self.login(url, 'user1')
                cred3 = self.login(url, 'user3')
                lcred = self.login(url, 'lecturer1')
                # Vote
                r = rq.get(url+'r/test_room_access', cookies=cred1)
                self.success(r)
                sid = r.json()['surveys'][0]['id']
                for opt in i:
                    self.ok(rq.post(url+'r/test_room_access/s/'+str(sid)+'/vote', json={'option': opt}, cookies=cred1))
                for opt in j:
                    self.ok(rq.post(url+'r/test_room_access/s/'+str(sid)+'/vote', json={'option': opt}, cookies=cred3))
                # Close survey
                self.ok(rq.post(url+'r/test_room_access/s/'+str(sid)+'/close', cookies=lcred))
                # Check result
                r = rq.get(url+'r/test_room_access', cookies=cred1)
                self.success(r)
                try:
                    self.json_match(r.json(), sample_json(sv=votes))
                except AssertionError as e:
                    e.args = (e.args[0]+'\nparams: {} {}\nexpected: {}\nresponse: {}'.format(i,j,votes,r.text),)
                    raise e


if __name__ == '__main__':
    main()

