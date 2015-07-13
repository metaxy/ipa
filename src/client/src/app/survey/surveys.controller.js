'use strict';
export default function SurveysCtrl($rootScope, $http, Shout, ApiUrl, $state) {
  //todo: this.my_rooms = Account.rooms({id: LoopBackAuth.currentUserId});
  $rootScope.siteTitle = "Umfragen";

  $http.get(ApiUrl+'/list_rooms')
  .success((data) => {
      this.my_rooms = data.rooms;
   })
  .error(() => {
      Shout.error("Could not get rooms");
  });
}
