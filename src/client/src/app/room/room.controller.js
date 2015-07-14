'use strict';
export default function RoomCtrl($scope, $stateParams, $interval, $rootScope) {
  $rootScope.siteTitle = $stateParams.roomId;
  this.speed = 0.5;

  this.updateSpeed = () => {
    /*Speed.current().$promise.then((data) => {
      this.speed = data.speed;
      if(this.speed >= 0.45 && this.speed <= 0.55) {
        this.speedName = "Ok so";
      } else if(this.speed > 0.55) {
        this.speedName = "schneller";
      } else {
        this.speedName = "langsamer";
      }
    });*/
  }
  this.updateSpeed();
  this.intervalPromise = $interval(this.updateSpeed, 5000);
  $scope.$on('$destroy', () => $interval.cancel(this.intervalPromise));
}
