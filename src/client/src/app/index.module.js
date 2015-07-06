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
import AdminCtrl from './admin/admin.controller';

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
  .controller('AdminCtrl', AdminCtrl)
  .provider('LfAcl', LfAcl)
  .factory('Shout', Shout)
  .constant('ApiUrl', 'http://localhost:5000/api')
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
        url: '/room_survey/:surveyId',
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
        url: '/survey/room/:roomId',
        templateUrl: 'app/survey/survey.html',
        controller: 'SurveyCtrl as surveyCtrl',
        acl: {
          needRights: ['create_survey']
        }
      })
      .state('survey_view', {
        url: '/survey/view/:surveyId',
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
        url: '/user_edit/:userId',
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

    $urlRouterProvider.otherwise('/');
    //$locationProvider.html5Mode(true)
  })

  .run(($rootScope, $state, LfAcl, $http, ApiUrl) => {
    $rootScope.$state = $state; // state to be accessed from view
    LfAcl.setRightsPromise($http.get(ApiUrl+'/list_permissions'));
    $rootScope.acl = LfAcl;
  });

