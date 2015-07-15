'use strict';
export default function SurveysCtrl($rootScope, $http, Shout, ApiUrl, $state) {
  $rootScope.siteTitle = "Umfragen";
  $http.get(ApiUrl+'/list_rooms')
    .success((data) => this.rooms = data.rooms)
    .error(() => Shout.error("Could not get rooms"));
}
