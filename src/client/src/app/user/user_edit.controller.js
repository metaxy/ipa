'use strict';
export default function UserCtrl(Account, $stateParams, $state, $rootScope) {
  $rootScope.siteTitle = "User editieren";
  this.user = Account.findById({id: $stateParams.userId});
  
  this.save = () => {
    Account.upsert(this.user);
  }
  this.delete = () => {
    Account.deleteById({id: $stateParams.userId});
    $state.go('user');
  }
  
}