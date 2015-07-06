'use strict';
export default function RoomSurveyCtrl($stateParams, Room, $interval, $scope) {
  this.surveys = [];
  
  this.update = () => {
    Room.survey({id: $stateParams.roomId}, {filter:{where: {open: true}}})
      .$promise.then((data) => this.surveys = data);
  }
  
  this.update();
  this.intervalPromise = $interval(this.update, 4000);
  $scope.$on('$destroy', () => $interval.cancel(this.intervalPromise));
}