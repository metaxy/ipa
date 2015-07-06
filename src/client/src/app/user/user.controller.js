'use strict';
export default function UserCtrl($rootScope) {
  this.users = Account.find();

  $rootScope.siteTitle = "Benutzer";

  this.delete = (user_id) => {
    //todo: Account.deleteById({id: user_id});
  }

}
