'use strict';
import _ from 'lodash';

export default function LfAcl() {
  var self = {};
 
  self.rights = false;
  self.rightsPromise = false;
  self.redirect = 'login';

  self.contains = (list, item) => _.contains(list, item);

  self.isGranted = (actions) =>  _.every(actions, (i) => self.contains(self.rights, i))
 
  self.isNotGranted = (actions) => !self.isGranted(actions);
  
  
  this.$get = ['$q', '$rootScope', '$state', function($q, $rootScope, $state) {
    var acl = {};

    acl.setRedirect = (redirect) => self.redirect = redirect;
    acl.student = ['view_index',
            'view_room',
            'create_question',
            'join_lecture',
            'vote_tempo',
            'vote_question',
            'vote_survey']
            
    acl.lecturer = [
            'manage_lecture',
            'create_survey',
            'create_room',
            'view_tempo',
            'close_survey',
            'delete_question'];
    acl.admin = [
            'create_account',
            'delete_account',
            'assign_role',
            'create_role',
            'edit_role',
            'delete_role'];
    acl.allRights = acl.student.concat(acl.lecturer.concat(acl.admin))
    acl.setRights = (rights) => self.rights = rights;
    acl.setRightsPromise = (rightsPromise) => {
      self.rightsPromise = rightsPromise;
      self.rightsPromise
        .then(
          (data) => {
            self.rights = data.roles;
            console.log(self.rights);
            $rootScope.acl = acl;
          },
          (err) => {
            self.rights = [];
            $rootScope.acl = acl;
            $state.go(self.redirect);
          }
        );

    };

    $rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams) {
      console.log("state change");
      if (self.rights === false) {
        self.rightsPromise
        .success(
          (data) => {
            self.rights = data.roles;
            $rootScope.acl = acl;
            acl.changeState(event, toState);
          }
         )
        .error(
          (err) => {
            self.rights = acl.allRights;
            $rootScope.acl = acl;
            acl.changeState(event, toState);
          }
        );
      } else { //we have a reponse from loopback and we can check whether the user is allowed to do that
        acl.changeState(event, toState);
      }
    });

    acl.changeState = (event, toState) => {
      if (!toState.acl || !toState.acl.needRights) {
        return acl;
      }
      console.log(self.rights);
      var isGranted = self.isGranted(toState.acl.needRights);
      if (!isGranted && self.redirect !== false) {
        event.preventDefault();
        if (self.redirect !== toState.name) {
          $state.go(self.redirect);
        }
      }
    };

    acl.isLoggedOut = () => false /*!self.right || self.right.length == 0*/
    acl.isLoggedIn = () =>  true /*self.right && self.right.length > 0*/
    acl.can = (action) => self.isGranted([action]);
    acl.canAll = (actions) => self.isGranted(actions);
    acl.canAny = (actions) =>  _.any(actions, (i) => self.contains(self.rights, i));

    return acl;

  }];
}
