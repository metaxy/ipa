'use strict';
export default function UserCtrl($rootScope, $http, ApiUrl, Shout) {
  $rootScope.siteTitle = "Benutzer";

  this.reload = () => {
    $http.get(ApiUrl+'/list_users').success((data) => this.users = data.users);
  }

  this.reload();
  this.delete = (user_name) => {
    $http.post(ApiUrl+'/delete_account', {name : user_name})
      .success(() => this.reload())
      .error((err) => Shout.error(err));
  }

  this.createAccount = (account_name, account_password) => {
    $http.post(ApiUrl+'/create_account', {name : account_name, password: account_password})
      .success((data) => {
        Shout.success('Account created');
        this.reload();
      })
      .error((err) => {
        Shout.error('Could not create account');
      });
  }
}
