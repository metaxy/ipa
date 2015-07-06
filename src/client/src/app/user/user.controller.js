'use strict';
export default function UserCtrl(Account, $rootScope) {
  this.users = Account.find();

  $rootScope.siteTitle = "Benutzer";

  this.delete = (user_id) => {
    Account.deleteById({id: user_id});
  }

}
