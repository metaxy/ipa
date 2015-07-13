Server REST API documentation
=============================

.. WARNING! THIS FILE IS GENERATED AUTOMATICALLY FROM 'server.py' AND *WILL* BE
.. OVERWRITTEN. DO NOT EDIT!

assign_role
===========

:Routes:
    ``/api/assign_role``
:HTTP method:    POST
:Request JSON:
  ::

    {'name' : 'name_of_the_user',
     'role' : 'role_you_want_the_user_to_assign'}
:Response JSON:  ``{'return': 'ok'}``

close_survey
============

:Routes:
    ``/api/r/<room_name>/s/<int:survey_id>/close``
:HTTP method: POST
:Request POST data: None
:Response JSON: ``{"result": "ok"}``

create_account
==============

:Routes:
    ``/api/create_account``
:HTTP method:    POST
:Request JSON:
  ::

    {'name':     'name_of_the_user_you_want_to_create',
     'password': 'password_for_this_user'}

:Response JSON:  ``{'return': 'ok'}``

create_question
===============

:Routes:
    ``/api/r/<room_name>/create_question``
:HTTP method:   POST
:Request JSON:  ``{"text": "How do this works?"}``
:Response JSON: ``{"result": "ok"}``

create_role
===========

:Routes:
    ``/api/create_role``
:HTTP method:   POST
:Request JSON:  ``{'role': 'role_you_want_to_create' }``

                The permissions are set to ``DEFAULT_PARTICIPANT`` on role creation
:Response JSON: ``{'return': 'ok'}``

create_room
===========

:Routes:
    ``/api/create_room``
:HTTP method:   POST
:Request JSON:
  ::

    {'name'   :   'name_of_the_room_you_want_to_create',
     'passkey':   'passkey_for_this_room'}
:Response:      redirect to view_room

create_survey
=============

:Routes:
    ``/api/r/<room_name>/create_survey``
:HTTP method:   POST
:Request JSON: 
  ::

    {"title":   "test 1",
     "options": ["Something", "Option 2", "This is an example"]}
:Response JSON: ``{"result": "ok"}``

delete_account
==============

:Routes:
    ``/api/delete_account``
:HTTP method:    POST
:Request JSON: `` {'name': 'name_of_the_account_to_delete'}``
:Response JSON:  ``{'return': 'ok'}``

delete_question
===============

:Routes:
    ``/api/r/<room_name>/q/<int:question_id>/delete``
:HTTP method:       POST
:Request POST data: None
:Response JSON:     ``{"result": "ok"}``

delete_role
===========

:Routes:
    ``/api/delete_role``
:HTTP method: POST
:Request JSON: ``{"role": "role_to_delete"}``

delete_survey
=============

:Routes:
    ``/api/r/<room_name>/s/<int:survey_id>/delete``
:HTTP method:       POST
:Request POST data: None
:Response JSON:     ``{"result": "ok"}``

edit_role
=========

:Routes:
    ``/api/role/<role_name>``
	:HTTP method: POST
	:Request JSON: ``{"perms": ["complete", "updated", "list", "of", "permissions"]}``
    :Response JSON: ``{"result": "ok"}``

enter_room
==========

:Routes:
    ``/api/r/<room_name>/enter``
:HTTP method:   POST
:Request JSON:  ``{"passkey": "passkey_for_this_room"}``
:Response JSON: ``{"result": "ok"}``

leave_room
==========

:Routes:
    ``/api/r/<room_name>/leave_room``
:HTTP method:        POST
:Request POST data:  None
:Response JSON:      ``{"result": "ok"}``

list_permissions
================

:Routes:
    ``/api/list_permissions``
:HTTP method: GET
:Response JSON: ``{"perms": ["some_permission", "another_permission"]}``

list_roles
==========

:Routes:
    ``/api/list_roles``
:HTTP method: GET
:Response JSON:
  ::
    {"roles": [
        {"name":  "role_name",
         "perms": ["list", "of", "perms"]},
        {"name":  "another_role",
         "perms": ["perm1", "perm2"]}]}

list_rooms
==========

:Routes:
    ``/api/list_rooms``
:HTTP method:   GET
:Response JSON: ``{"rooms": ["some_room", "another_room"]}``

list_users
==========

:Routes:
    ``/api/list_users``
:HTTP method: GET
:Response JSON:
  ::
    {"users": [
        {"name": "some_username",
         "role": "that_users_role"},
        {"name": "another_name",
         "role": "some_role"}]}

login
=====

:Routes:
    ``/api/login``
:HTTP method:    POST
:Request JSON:
  ::

    {'uid':      'name_of_the_user_for_login',
     'password': 'password_of_this_user'}

:Response JSON:  ``{'return': 'ok', 'first_login': false}``

logout
======

:Routes:
    ``/api/logout``
:HTTP method:    POST
:Request POST data:  None
:Response JSON:  ``{'return': 'ok'}``

view_room
=========

:Routes:
    ``/api/r/<room_name>``
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
     "user_is_lecturer": False}

vote_question
=============

:Routes:
    ``/api/r/<room_name>/q/<int:question_id>/vote``
:HTTP method: POST
:Request POST data: None
:Response JSON: ``{"result": "ok"}``

vote_survey
===========

:Routes:
    ``/api/r/<room_name>/s/<int:survey_id>/vote``
:HTTP method:   POST
:Request JSON:  ``{"option": 3}``
:Response JSON: ``{"result": "ok"}``
