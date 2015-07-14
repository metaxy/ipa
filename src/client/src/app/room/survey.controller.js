'use strict';
export default function RoomSurveyCtrl($stateParams, $interval, $scope, $http, Shout, ApiUrl) {

  this.surveys = [];

  $http.get(ApiUrl+'/r/'+$stateParams.roomId)
  .success((data) => {
      this.surveys = data.surveys;
   })
  .error(() => {
      Shout.error("Could not get surveys");
  });
  
  this.update = () => {
  	// todo:
    /*Room.survey({id: $stateParams.roomId}, {filter:{where: {open: true}}})
      .$promise.then((data) => this.surveys = data);*/
  }
  
  this.update();
  this.intervalPromise = $interval(this.update, 4000);
  $scope.$on('$destroy', () => $interval.cancel(this.intervalPromise));
}