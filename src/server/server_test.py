
import time
from os.path import join, dirname, realpath
from unittest import TestCase, main
from tempfile import NamedTemporaryFile
from functools import wraps
from contextlib import contextmanager
from subprocess import *
import textwrap
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
def test_for(endpoint, doc=""):
    def deco(f):
        test_endpoints[endpoint] = (f, textwrap.dedent(doc).lstrip('\n').rstrip())
        return f
    return deco


ignore = lambda x: True
def sample_json(test, qv=0, sv=None, lect=False):
    case = lambda name, val: val if test==name else ignore
    cases = lambda d: d.get(test, ignore)
    opts = ['opt1', 'opt2', 'opt3']
    return {
        'name': case('basic', 'test_room_access'),
        'questions': cases({
            'questions': [{
                'id': ignore,
                'text': 'test question',
                'votes': qv
                }],
            'noquestions': []}),
        'surveys': cases({
            'surveys': [
                    {'id': ignore,
                     'title': 'test survey',
                     'options': opts,
                     'results': set(zip(opts, sv)),
                     'total': sum(sv),
                     'closed': True}
                if sv else
                    {'id': ignore,
                     'title': 'test survey',
                     'options': opts,
                     'closed': False}],
            'nosurveys': []}),
        'user_is_lecturer': case('basic', lect)
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

    def json(self, r, pat):
        self.success(r)
        self._json_match(r.json(), pat)

    def _json_match(self, d, pat, _path='root'):
        if isinstance(pat, dict):
            for k,v in pat.items():
                self.assertIn(k, d)
                self._json_match(d[k], v, _path+'/'+k)
            self._json_match(len(d), len(pat))
        elif isinstance(pat, list):
            self._json_match(len(d), len(pat))
            for i,(a,b) in enumerate(zip(d, pat)):
                self._json_match(a, b, _path+'['+str(i)+']')
        elif isinstance(pat, set) and not isinstance(d, set):
            if not isinstance(d, list):
                d = set(d)
            else:
                d = { e if isinstance(e, str) else tuple(e) for e in d }
            self._json_match(d, pat)
        elif callable(pat):
            self._json_match(pat(d), True)
        else:
            try:
                self.assertEqual(d, pat)
            except AssertionError as e:
                e.args = (e.args[0]+'\nat path: '+_path,)
                raise e


    def testUnitTestCoverage(self):
        with testserver() as url:
            """tests whether there is a unit test for every endpoint"""
            excluded_eps = {'static', 'view_index', 'gc_tempo_viewfunc'}
            eps = {rule.endpoint for rule in server.app.url_map.iter_rules()} - excluded_eps
            self.assertSetEqual(eps, set(test_endpoints.keys()))

    @test_for('login', """
    :HTTP method:    POST
    :Request JSON:
      ::

        {'uid':      'name_of_the_user_for_login',
         'password': 'password_of_this_user'}

    :Response JSON:  ``{'return': 'ok', 'first_login': false}`` """)
    def testLogin(self):
        with testserver() as url:
            self.denied (rq.post(url+'login', json={'uid': 'test1', 'password': 'invalid password'}))
            self.denied (rq.post(url+'login', json={'uid': 'test1', 'password': ''}))
            self.denied (rq.post(url+'login', json={'uid': '', 'password': 'invalid password'}))
            self.ok     (rq.post(url+'login', json={'uid': 'test1', 'password': 'test1'}))

    @test_for('delete_account', """
    :HTTP method:    POST
    :Request JSON: `` {'name': 'name_of_the_account_to_delete'}``
    :Response JSON:  ``{'return': 'ok'}`` """)
    def testDeleteAccount(self):
        with testserver() as url:
            r = rq.post(url+'login', json={'uid': 'test1', 'password': 'test1'})
            self.json(r, {'result': 'ok', 'first_login': True})

            r = rq.post(url+'login', json={'uid': 'test1', 'password': 'test1'})
            self.json(r, {'result': 'ok', 'first_login': False})

            self.ok(rq.post(url+'delete_account', json={'name': 'test1'}, cookies=self.login(url, 'admin')))

            r = rq.post(url+'login', json={'uid': 'test1', 'password': 'test1'})
            self.json(r, {'result': 'ok', 'first_login': True})
    
    
    @test_for('logout', """
    :HTTP method:    POST
    :Request POST data:  None
    :Response JSON:  ``{'return': 'ok'}`` """)
    def testLogout(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            
            self.ok     (rq.post(url+'logout', cookies=cred))
            
    @test_for('create_account', """
    :HTTP method:    POST
    :Request JSON:
      ::

        {'name':     'name_of_the_user_you_want_to_create',
         'password': 'password_for_this_user'}

    :Response JSON:  ``{'return': 'ok'}`` """)
    def testCreateAccount(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.denied   (rq.post(url+'create_account', json={'name': 'create_test1', 'password': 'create_test1'}, cookies=cred))
            
            cred = self.login(url, 'lecturer1')
            self.denied   (rq.post(url+'create_account', json={'name': 'create_test1', 'password': 'create_test1'}, cookies=cred))
            
            cred = self.login(url, 'admin')
            self.ok       (rq.post(url+'create_account', json={'name': 'create_test1', 'password': ''}, cookies=cred))
            self.conflict (rq.post(url+'create_account', json={'name': 'create_test1', 'password': ''}, cookies=cred))
    
    @test_for('assign_role', """ 
    :HTTP method:    POST
    :Request JSON:
      ::
      
        {'name' : 'name_of_the_user',
         'role' : 'role_you_want_the_user_to_assign'}
    :Response JSON:  ``{'return': 'ok'}`` """)
    def testAssignRole(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.denied   (rq.post(url+'assign_role', json={'name': 'lecturer1', 'role': 'participant'}, cookies=cred))
            
            cred = self.login(url, 'lecturer1')
            self.denied   (rq.post(url+'assign_role', json={'name': 'user1', 'role': 'participant'}, cookies=cred))
            
            cred = self.login(url, 'admin')
            self.notfound (rq.post(url+'assign_role', json={'name': 'user_do_not_exist', 'role': 'participant'}, cookies=cred))
            self.notfound (rq.post(url+'assign_role', json={'name': 'user1', 'role': 'role_do_not_exist'}, cookies=cred))
            self.ok       (rq.post(url+'assign_role', json={'name': 'user1', 'role': 'participant'}, cookies=cred))
    
    @test_for('create_role', """
    :HTTP method:   POST
    :Request JSON:  ``{'role': 'role_you_want_to_create' }``

                    The permissions are set to ``DEFAULT_PARTICIPANT`` on role creation
    :Response JSON: ``{'return': 'ok'}`` """)
    def testCreateRole(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.denied   (rq.post(url+'create_role', json={'role': 'role_test'}, cookies=cred))
            
            cred = self.login(url, 'lecturer1')
            self.denied   (rq.post(url+'create_role', json={'role': 'role_test'}, cookies=cred))
            
            cred = self.login(url, 'admin')
            self.ok       (rq.post(url+'create_role', json={'role': 'role_test'}, cookies=cred))
            self.conflict (rq.post(url+'create_role', json={'role': 'role_test'}, cookies=cred))
    
    @test_for('create_room', """
    :HTTP method:   POST
    :Request JSON:
      ::

        {'name'   :   'name_of_the_room_you_want_to_create',
         'passkey':   'passkey_for_this_room'}
    :Response:      redirect to view_room """)
    def testCreateRoom(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.denied     (rq.post(url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.success    (rq.post(url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))
            self.success    (rq.post(url+'create_room', json={'name': 'ünicödeが好き！', 'passkey': 'testpass1'}, cookies=cred))
            self.conflict   (rq.post(url+'create_room', json={'name': 'create_test1', 'passkey': ''}, cookies=cred))

    @test_for('enter_room', """
    :HTTP method:   POST
    :Request JSON:  ``{"passkey": "passkey_for_this_room"}``
    :Response JSON: ``{"result": "ok"}`` """)
    def testEnterRoom(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.denied (rq.get (url+'r/test_room_deny', cookies=cred))
            self.ok     (rq.post(url+'r/test_room_deny/enter', json={'passkey': 'test_passkey'}, cookies=cred))
            self.success(rq.get (url+'r/test_room_deny', cookies=cred))
            
    @test_for('leave_room', """
    :HTTP method:        POST
    :Request POST data:  None
    :Response JSON:      ``{"result": "ok"}`` """)
    def TestLeaveRoom(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            
            self.ok     (rq.post(url+'r/test_room_access/leave_room', cookies=cred))
            

    @test_for('create_survey', """
    :HTTP method:   POST
    :Request JSON: 
      ::

        {"title":   "test 1",
         "options": ["Something", "Option 2", "This is an example"]}
    :Response JSON: ``{"result": "ok"}`` """)
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

    @test_for('close_survey', """
    :HTTP method:       POST
    :Request POST data: None
    :Response JSON:     ``{"result": "ok"}`` """)
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

    @test_for('delete_survey', """
    :HTTP method:       POST
    :Request POST data: None
    :Response JSON:     ``{"result": "ok"}`` """)
    def testDeleteSurvey(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.json(r, sample_json('surveys'))
            sid = r.json()['surveys'][0]['id']

            self.denied  (rq.post(url+'r/test_room_access/s/'+str(sid)+'/delete', cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.ok      (rq.post(url+'r/test_room_access/s/'+str(sid)+'/delete', cookies=cred))
            self.json(rq.get(url+'r/test_room_access', cookies=cred), sample_json('nosurveys'))

            self.notfound(rq.post(url+'r/test_room_access/s/123456789/delete', cookies=cred))

    @test_for('create_question', """
    :HTTP method:   POST
    :Request JSON:  ``{"text": "How do this works?"}``
    :Response JSON: ``{"result": "ok"}`` """)
    def testCreateQuestion(self):
        with testserver() as url:
            cred = self.login(url, 'user2')
            self.denied(rq.post(url+'r/test_room_access/create_question', json={'text': 'test 1'}, cookies=cred))
            
            cred = self.login(url, 'user1')
            self.ok      (rq.post(url+'r/test_room_access/create_question', json={'text': 'test 2'}, cookies=cred))
            self.notfound(rq.post(url+'r/unknown_room/create_question', json={'text': 'test 3'}, cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.ok(rq.post(url+'r/test_room_access/create_question', json={'text': 'test 4'}, cookies=cred))

    @test_for('delete_question', """
    :HTTP method:       POST
    :Request POST data: None
    :Response JSON:     ``{"result": "ok"}`` """)
    def testDeleteQuestion(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.json(r, sample_json('questions'))
            qid = r.json()['questions'][0]['id']

            self.denied  (rq.post(url+'r/test_room_access/q/'+str(qid)+'/delete', cookies=cred))

            cred = self.login(url, 'lecturer1')
            self.ok      (rq.post(url+'r/test_room_access/q/'+str(qid)+'/delete', cookies=cred))
            self.json(rq.get(url+'r/test_room_access', cookies=cred), sample_json('noquestions'))
            self.notfound(rq.post(url+'r/test_room_access/q/123456789/delete', cookies=cred))

    @test_for('list_rooms', """
    :HTTP method:   GET
    :Response JSON: ``{"rooms": ["some_room", "another_room"]}`` """)
    def testListRooms(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            r = rq.get(url+'list_rooms', cookies=cred)
            self.json(r, {'rooms': {'test_room_access', 'test_room_deny'}})

    @test_for('view_room', """
    :HTTP method:   GET
    :Response JSON:
      ::

        {"name": "some_test_room"
         "questions": [{
               "id": ignore,
               "text": "test question",
               "votes": 23
            }],
         "surveys": [
            {"id": 1,
             "title": "Open survey",
             "options": ["foo", "bar", "third option"],
             "closed": false},
            {"id": 2,
             "title": "Closed survey",
             "options": ["baz", "something"],
             "results": [["baz", 23], ["something", 42]]),
             "total": 65,
             "closed": true}],
         "user_is_lecturer": False} """)
    def testViewRoom(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            self.notfound(rq.get (url+'r/a_room_that_does_not_exist', cookies=cred))

            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.json(r, sample_json('basic'))

            cred = self.login(url, 'lecturer1')
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.success(r)
            j = r.json()
            self.assertEqual(True, j['user_is_lecturer'])

            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.json(r, sample_json('basic', lect=True))

    @test_for('vote_question', """
    :HTTP method: POST
    :Request POST data: None
    :Response JSON: ``{"result": "ok"}`` """)
    def testVoteQuestion(self):
        with testserver() as url:
            cred = self.login(url, 'user1')
            # Vote
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.json(r, sample_json('questions'))
            qid = r.json()['questions'][0]['id']
            self.ok(rq.post(url+'r/test_room_access/q/'+str(qid)+'/vote', cookies=cred))
            # Check result
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.json(r, sample_json('questions', qv=1))
            # Vote again
            self.ok(rq.post(url+'r/test_room_access/q/'+str(qid)+'/vote', cookies=cred))
            # Check result again
            r = rq.get(url+'r/test_room_access', cookies=cred)
            self.json(r, sample_json('questions', qv=1))

    @test_for('vote_survey', """
    :HTTP method:   POST
    :Request JSON:  ``{"option": 3}``
    :Response JSON: ``{"result": "ok"}`` """)
    def testVoteSurvey(self):
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
                r = rq.get(url+'r/test_room_access', cookies=lcred)
                self.json(r, sample_json('surveys', sv=votes))

    @test_for('close_survey', """
    :HTTP method: POST
    :Request POST data: None
    :Response JSON: ``{"result": "ok"}`` """)
    def testCloseSurvey(self):
        with testserver() as url:
            lcred = self.login(url, 'lecturer1')
            r = rq.get(url+'r/test_room_access', cookies=lcred)
            self.success(r)
            sid = r.json()['surveys'][0]['id']
            # Close survey
            self.ok(rq.post(url+'r/test_room_access/s/'+str(sid)+'/close', cookies=lcred))
            # Check result
            r = rq.get(url+'r/test_room_access', cookies=lcred)
            self.json(r, sample_json('surveys', sv=(0, 0, 0)))

    @test_for('list_permissions', """
    :HTTP method: GET
    :Response JSON: ``{"perms": ["some_permission", "another_permission"]}`` """)
    def testListPermissions(self):
        with testserver() as url:
            participant_perms   = {server.Perms(p).name for p in server.Perms._participant.value}
            lecturer_perms      = {server.Perms(p).name for p in server.Perms._lecturer.value}
            admin_perms         = {server.Perms(p).name for p in server.Perms._admin_only.value}

            cred = self.login(url, 'user1')
            r = rq.get(url+'list_permissions', cookies=cred)
            self.json(r, {'perms': participant_perms})

            cred = self.login(url, 'lecturer1')
            r = rq.get(url+'list_permissions', cookies=cred)
            self.json(r, {'perms': lecturer_perms | participant_perms})

            cred = self.login(url, 'admin')
            r = rq.get(url+'list_permissions', cookies=cred)
            self.json(r, {'perms': admin_perms | lecturer_perms | participant_perms})
    
    @test_for('list_users', """
    :HTTP method: GET
    :Response JSON:
      ::
        {"users": [
            {"name": "some_username",
             "role": "that_users_role"},
            {"name": "another_name",
             "role": "some_role"}]}""")
    def testListUsers(self):
        with testserver() as url:
            cred = self.login(url, 'admin')
            r = rq.get(url+'list_users', cookies=cred)
            self.success(r)
            j = r.json()
            testdata = [('user1'     ,'participant'),
                        ('user2'     ,'participant'),
                        ('user3'     ,'participant'),
                        ('lecturer1' ,'lecturer'),
                        ('admin'     ,'admin')]
            self._json_match(j, {'users': [{'name': ignore, 'role': ignore}]*len(testdata)})
            j['users'] = {e['name']: e for e in j['users']}
            self._json_match(j, {'users': {n: {'name': n, 'role': r} for n,r in testdata}})


    @test_for('delete_role', """
    :HTTP method: POST
    :Request JSON: ``{"role": "role_to_delete"}``""")
    def testDeleteRole(self):
        with testserver() as url:
            rl = lambda r: {role['name'] for role in r.json()['roles']}

            cred = self.login(url, 'admin')
            roles = rl(rq.get(url+'list_roles', cookies=cred))
            self.assertIn('lecturer', roles)

            self.conflict(rq.post(url+'delete_role', json={'role': 'lecturer'}, cookies=cred))
            self.ok(rq.post(url+'assign_role', json={'name': 'lecturer1', 'role': 'participant'}, cookies=cred))

            self.ok(rq.post(url+'delete_role', json={'role': 'lecturer'}, cookies=cred))
            self.assertSetEqual(rl(rq.get(url+'list_roles', cookies=cred)), roles - {'lecturer'})

    @test_for('edit_role', """
    :HTTP method: POST
    :Request JSON: ``{"perms": ["complete", "updated", "list", "of", "permissions"]}``
    :Response JSON: ``{"result": "ok"}`` """)
    def testEditRole(self):
        with testserver() as url:
            rl = lambda r: {role['name']: role for role in r.json()['roles']}

            cred = self.login(url, 'admin')
            perms = set(rl(rq.get(url+'list_roles', cookies=cred))['lecturer']['perms'])
            self.assertIn('create_room', perms)
            self.assertIn('view_room', perms)
            self.assertNotIn('create_role', perms)

            newperms = perms | {'create_role'} - {'view_room', 'create_room'}

            self.ok(rq.post(url+'role/lecturer', json={'perms': list(newperms)}, cookies=cred))

            perms = set(rl(rq.get(url+'list_roles', cookies=cred))['lecturer']['perms'])
            self.assertSetEqual(perms, newperms)

    @test_for('list_roles', """
    :HTTP method: GET
    :Response JSON:
      ::
        {"roles": [
            {"name":  "role_name",
             "perms": ["list", "of", "perms"]},
            {"name":  "another_role",
             "perms": ["perm1", "perm2"]}]}""")
    def testListRoles(self):
        with testserver() as url:
            participant_perms   = {server.Perms(p).name for p in server.Perms._participant.value}
            lecturer_perms      = {server.Perms(p).name for p in server.Perms._lecturer.value}
            admin_perms         = {server.Perms(p).name for p in server.Perms._admin_only.value}

            cred = self.login(url, 'admin')
            r = rq.get(url+'list_roles', cookies=cred)
            self.success(r)
            j = r.json()
            testdata = [('participant', participant_perms),
                        ('lecturer',    lecturer_perms | participant_perms),
                        ('admin',       admin_perms | lecturer_perms | participant_perms)]
            self._json_match(j, {'roles': [{'name': ignore, 'perms': ignore}]*len(testdata)})
            j['roles'] = {e['name']: e for e in j['roles']}
            self._json_match(j, {'roles': {n: {'name': n, 'perms': p} for n,p in testdata}})
    
    @test_for('vote_tempo', """
    :HTTP method: GET
    :Request JSON: None
    :Response JSON: ``{"result": "ok"}`` """)
    @test_for('view_tempo', """
    :HTTP method: GET
    :Response JSON: ``{"up": 23, "down": 42}``
                    
                    The vote count is by default measured over the last five minutes.
    """)
    def testTempoStuff(self):
        with testserver() as url:
            cred = self.login(url, 'lecturer1')
            self.bad(rq.post(url+'r/test_room_access/t/this_does_not_exist', cookies=cred))
            self.ok(rq.post(url+'r/test_room_access/t/up', cookies=cred))
            self.ok(rq.post(url+'r/test_room_access/t/down', cookies=cred))
            self.ok(rq.post(url+'r/test_room_access/t/down', cookies=cred))

            self.json(rq.get(url+'r/test_room_access/t', cookies=cred), {'up': 1, 'down': 2})
            time.sleep(2)
            self.ok(rq.post(url+'r/test_room_access/t/up', cookies=cred))
            self.json(rq.get(url+'r/test_room_access/t', cookies=cred), {'up': 2, 'down': 2})
            self.ok(rq.post(url+'gc_tempo', json={'timeout': 1}, cookies=cred))
            self.json(rq.get(url+'r/test_room_access/t', cookies=cred), {'up': 1, 'down': 0})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--apidoc',
            help="Generate API endpoint doc as restructuredtext",
            type=str,
            nargs='?',
            default=False)
    args = parser.parse_args()
    if args.apidoc is not False:
        with open(args.apidoc or 'api-doc.rst', 'w') as f:
            f.write(textwrap.dedent("""\
                    Server REST API documentation
                    =============================
                    
                    .. WARNING! THIS FILE IS GENERATED AUTOMATICALLY FROM 'server.py' AND *WILL* BE
                    .. OVERWRITTEN. DO NOT EDIT!
                    """))
            for endpoint, (_f, doc) in sorted(test_endpoints.items()):
                routes = """
                    """.join('``'+rule.rule+'``'
                            for rule in server.app.url_map.iter_rules()
                            if rule.endpoint == endpoint)
                f.write(textwrap.dedent("""
                    {endpoint}
                    {endpoint_ul}

                    :Routes:
                        {routes}
                    {doc}
                    """).format(endpoint=endpoint,
                        endpoint_ul="="*len(endpoint),
                        routes=routes,
                        doc=doc))
    else: 
        main()

