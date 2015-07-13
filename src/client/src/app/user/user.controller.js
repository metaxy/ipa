'use strict';
export default function UserCtrl($rootScope, $http, ApiUrl) {

  $rootScope.siteTitle = "Benutzer";

  this.reload = () => {
    this.users = $http.get(ApiUrl+'/list_users');
  }

  this.reload();
  this.delete = (user_name) => {
    $http.post(ApiUrl+'/delete_account', {name : user_name})
      .success(() => this.reload())
      .error((err) => Shout.error(err));
  }

}
