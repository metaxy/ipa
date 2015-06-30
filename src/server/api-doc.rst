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

    {'name': 'name_of_the_user',
     'role': 'role_you_want_the_user_to_assign'}
:Response JSON:  ``{'return': 'ok'}``

close_survey
============

:Routes:
    ``/api/r/<room_name>/s/<int:survey_id>/close``


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


create_role
===========

:Routes:
    ``/api/create_role``
:HTTP method:   POST
:Request JSON:  ``{'role': 'role_you_want_to_create' }``

                The permissions set to DEFAULT_PARTICIPANT on role creation
:Response JSON: ``{'return': 'ok'}``

create_room
===========

:Routes:
    ``/api/create_room``
:HTTP method:   POST
:Request JSON:
  ::

    {'name':   'name_of_the_room_you_want_to_create',
    'passkey': 'passkey_for_this_room'}
:Response:      redirect to view_room

create_survey
=============

:Routes:
    ``/api/r/<room_name>/create_survey``


delete_question
===============

:Routes:
    ``/api/r/<room_name>/q/<int:question_id>/delete``


enter_room
==========

:Routes:
    ``/api/r/<room_name>/enter``


list_rooms
==========

:Routes:
    ``/api/list_rooms``


login
=====

:Routes:
    ``/api/login``
:HTTP method:    POST
:Request JSON:
  ::

    {'uid':      'name_of_the_user_for_login',
     'password': 'password_of_this_user'}

:Response JSON:  ``{'return': 'ok'}``

view_room
=========

:Routes:
    ``/api/r/<room_name>``


vote_question
=============

:Routes:
    ``/api/r/<room_name>/q/<int:question_id>/vote``


vote_survey
===========

:Routes:
    ``/api/r/<room_name>/s/<int:survey_id>/vote``

