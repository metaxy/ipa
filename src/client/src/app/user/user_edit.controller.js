'use strict';
export default function UserCtrl($stateParams, $state, $rootScope, $http, ApiUrl) {
  $rootScope.siteTitle = "User editieren";
  this.user = {}
  $http.get(ApiUrl+'/list_users')
    .success((data) => {
      for(let user of data.users) {
        if(user.name === $stateParams.userName) {
          this.user = user;
        }
      }
     })
    .error(() => Shout.error("Could not get users"));

  $http.get(ApiUrl+'/list_roles')
    .success((data) => this.roles = data.roles)
    .error((err) => Shout.error("Could not get roles"));


  this.save = () => {
    $http.post(ApiUrl+'/assign_role', {name : this.user.name,role: this.user.role})
      .success((data) => $state.go('users'))
      .error((err) => Shout.error(err));

    //TODO: save user (missing endpoint)
  }
  this.delete = () => {
    $http.post(ApiUrl+'/delete_account', {name : $stateParams.userName})
      .success(() => $state.go('users'))
      .error((err) => Shout.error(err));

  }
 }
