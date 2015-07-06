'use strict';
export default function NavbarCtrl($state, LfAcl, $http, ApiUrl) {
  this.logout = () => {
    $http.post(ApiUrl+'/logout').success(() => $state.go('login'));
  }
}