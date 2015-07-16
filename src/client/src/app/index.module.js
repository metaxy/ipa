import MainCtrl from './main/main.controller';
import NavbarCtrl from './components/navbar/navbar.controller';
import Shout from './components/shout';
import LfAcl from './auth/acl';
import LoginCtrl from './auth/login.controller';
import RoomCtrl from './room/room.controller';
import RoomSurveyCtrl from './room/survey.controller';
import SurveyVoteCtrl from './room/survey_vote.controller';
import SpeedCtrl from './room/speed.controller';
import QuestionCtrl from './room/question.controller';
import UserCtrl from './user/user.controller';
import UserEditCtrl from './user/user_edit.controller';
import SurveyCtrl from './survey/survey.controller';
import SurveysCtrl from './survey/surveys.controller';
import SurveyViewCtrl from './survey/survey_view.controller';
import RightsCtrl from './rights/rights.controller';
var allRights = ["create_question", "join_lecture", "vote_tempo", "vote_question", "vote_survey", "manage_lecture", "create_survey", "create_room", "view_tempo", "close_survey", "delete_question", "create_account", "delete_account", "assign_role", "create_role", "edit_role", "delete_role", "list_roles", "list_users"];


angular.module('lifi', ['ngAnimate', 'ngCookies', 'ngTouch',
               'ngSanitize', 'ngResource', 'ui.router', 'ngMaterial',
                'picardy.fontawesome', 'n3-pie-chart', 'toastr'])
  .controller('MainCtrl', MainCtrl)
  .controller('NavbarCtrl', NavbarCtrl)
  .controller('LoginCtrl', LoginCtrl)
  .controller('RoomCtrl', RoomCtrl)
  .controller('RoomSurveyCtrl', RoomSurveyCtrl)
  .controller('SpeedCtrl', SpeedCtrl)
  .controller('QuestionCtrl', QuestionCtrl)
  .controller('UserCtrl', UserCtrl)
  .controller('UserEditCtrl', UserEditCtrl)
  .controller('SurveyCtrl', SurveyCtrl)
  .controller('SurveysCtrl', SurveysCtrl)
  .controller('SurveyViewCtrl', SurveyViewCtrl)
  .controller('SurveyVoteCtrl', SurveyVoteCtrl)
  .controller('RightsCtrl', RightsCtrl)
  .provider('LfAcl', LfAcl)
  .factory('Shout', Shout)
  .constant('ApiUrl', 'http://localhost:8080/api')
  .constant('AllRights', allRights)
  .config(function ($stateProvider, $urlRouterProvider, $locationProvider, $mdThemingProvider, $httpProvider) {
    $httpProvider.defaults.withCredentials = true;
    $mdThemingProvider.theme('default')
    .primaryPalette('blue')
    .accentPalette('pink')
    .warnPalette('red')
    .backgroundPalette('grey');

    $stateProvider
      .state('home', {
        url: '/',
        templateUrl: 'app/main/main.html',
        controller: 'MainCtrl as mainCtrl',
        acl: {
          needRights: ['view_index']
        }
      })
      .state('room', {
        url: '/room/:roomId',
        templateUrl: 'app/room/room.html',
        controller: 'RoomCtrl as roomCtrl',
        acl: {
          needRights: ['join_lecture']
        }
      })
      .state('room_survey', {
        url: '/room_survey/:roomName/:surveyId',
        templateUrl: 'app/room/survey_vote.html',
        controller: 'SurveyVoteCtrl as surveyCtrl',
        acl: {
          needRights: ['join_lecture']
        }
      })
      .state('surveys', {
        url: '/surveys',
        templateUrl: 'app/survey/surveys.html',
        controller: 'SurveysCtrl as surveysCtrl',
        acl: {
          needRights: ['create_survey']
        }
      })
      .state('survey', {
        url: '/survey/room/:roomName',
        templateUrl: 'app/survey/survey.html',
        controller: 'SurveyCtrl as surveyCtrl',
        acl: {
          needRights: ['create_survey']
        }
      })
      .state('survey_view', {
        url: '/survey/view/:roomName/:surveyId',
        templateUrl: 'app/survey/survey_view.html',
        controller: 'SurveyViewCtrl as surveyCtrl',
        acl: {
          needRights: ['create_survey']
        }
      })
      .state('user', {
        url: '/user',
        templateUrl: 'app/user/user.html',
        controller: 'UserCtrl as userCtrl',
        acl: {
          needRights: ['create_account']
        }
      })
      .state('user_edit', {
        url: '/user_edit/:userName',
        templateUrl: 'app/user/user_edit.html',
        controller: 'UserEditCtrl as userCtrl',
        acl: {
          needRights: ['delete_account']
        }
      })
      .state('login', {
        url: '/login',
        templateUrl: 'app/auth/login.html',
        controller: 'LoginCtrl as loginCtrl',
        acl: {
          needRights: []
        }
      })
      .state('rights', {
        url: '/rights',
        templateUrl: 'app/rights/rights.html',
        controller: 'RightsCtrl as rightsCtrl',
        acl: {
          needRights: ['assign_role']
        }
      })

    $urlRouterProvider.otherwise('/');
    //$locationProvider.html5Mode(true)
  })

  .run(($rootScope, $state, LfAcl, $http, ApiUrl) => {
    $rootScope.$state = $state; // state to be accessed from view
    LfAcl.setRightsPromise($http.get(ApiUrl+'/list_permissions'));
    $rootScope.acl = LfAcl;
  });
