'use strict';
export default function RoomCtrl($scope, Room, $stateParams, Speed, $interval, $rootScope) {
  
  Room.findById({id: $stateParams.roomId}).$promise
    .then((data) => {
      $rootScope.siteTitle = data.name;
      return data;
    });
  this.speed = 0.5;

  this.updateSpeed = () => {
    Speed.current().$promise.then((data) => {
      this.speed = data.speed;
      if(this.speed >= 0.45 && this.speed <= 0.55) {
        this.speedName = "Ok so";
      } else if(this.speed > 0.55) {
        this.speedName = "schneller";
      } else {
        this.speedName = "langsamer";
      }
    });
  }
  this.updateSpeed();
  this.intervalPromise = $interval(this.updateSpeed, 5000);
  $scope.$on('$destroy', () => $interval.cancel(this.intervalPromise));
}
