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
:HTTP method:   POST

:Request JSON:  None

:Response JSON: ``{'result' : 'ok'}``

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
:Request JSON:  ``{'text': 'text_for_the_question' }``

:Response JSON: ``{'return': 'ok'}``

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

        {'title'   : 'title_for_the_new_survey',
         'options' : 'list_of_options_for_the_survey'}
:Response JSON: ``{'return': 'ok'}``

delete_question
===============

:Routes:
    ``/api/r/<room_name>/q/<int:question_id>/delete``
:HTTP method:   POST
:Request JSON:  None

:Response JSON: ``{'return': 'ok'}``

enter_room
==========

:Routes:
    ``/api/r/<room_name>/enter``
:HTTP method:   GET

:Request:       None

:Response JSON: 
    ::

        {'name'             : 'name_of_the_room',
         'questions'        : 'questions_of_the_room',
         'surveys'          : 'survey_of_the_room',
         'user_is_lecturer' : 'is_the_user_the_lecturer?'}

list_rooms
==========

:Routes:
    ``/api/list_rooms``
:HTTP method:   GET
:Request:       None

:Response JSON: ``{'rooms': 'list_of_all_rooms'}``

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
:HTTP method:   GET

:Request:       None

:Response JSON: 
    ::

        {'name'             : 'name_of_the_room',
         'questions'        : 'questions_of_the_room',
         'surveys'          : 'survey_of_the_room',
         'user_is_lecturer' : 'is_the_user_the_lecturer?'}

vote_question
=============

:Routes:
    ``/api/r/<room_name>/q/<int:question_id>/vote``
:HTTP method:   POST

:Request JSON:  None

:Response JSON: ``{'result' : 'ok'}``

vote_survey
===========

:Routes:
    ``/api/r/<room_name>/s/<int:survey_id>/vote``
:HTTP method:   POST

:Request JSON:  ``{'options': 'list_of_all_options'}`` 

:Response JSON: ``{'result' : 'ok'}``
