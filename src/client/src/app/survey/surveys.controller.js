'use strict';
export default function SurveysCtrl(Account, LoopBackAuth, $rootScope) {
  this.my_rooms = Account.rooms({id: LoopBackAuth.currentUserId});
  $rootScope.siteTitle = "Umfragen";
}