'use strict';
export default function SpeedCtrl($http, ApiUrl, $stateParams, $interval, $scope) {
  this.reload = () => {
    $http.get(ApiUrl+'/r/'+$stateParams.roomId+'/t')
      .success((data) => {
        this.up = data.up;
        this.down = data.down;
      })
      .error(() => Shout.error("Konnte die Geschwindigkeit nicht bekommen."));
  }
  this.reload();



  this.faster = () => {
    $http.post(ApiUrl + '/r/' + $stateParams.roomId + '/t/up');
  }

  this.slower = () => {
    $http.post(ApiUrl + '/r/' + $stateParams.roomId + '/t/down');
  }

  this.intervalPromise = $interval(this.reload, 5000);
  $scope.$on('$destroy', () => $interval.cancel(this.reload));


}
