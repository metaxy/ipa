'use strict';
export default function SpeedCtrl($http, ApiUrl, $stateParams, $interval, $scope) {
  this.reload = () => {
    $http.get(ApiUrl+'/r/'+$stateParams.roomId+'/t')
      .success((data) => {
        this.up = data.up;
        this.down = data.down;
        this.graph = [
        {label: "Schneller", value: data.up, color: '#76d11b'},
        {label: "Langsamer", value: data.down, color: '#de0000'}];
      })
      .error(() => Shout.error("Konnte die Geschwindigkeit nicht bekommen."));
  }
  this.reload();

  this.opt = {thickness: 20};


  this.faster = () => {
    $http.post(ApiUrl + '/r/' + $stateParams.roomId + '/t/up');
  }

  this.slower = () => {
    $http.post(ApiUrl + '/r/' + $stateParams.roomId + '/t/down');
  }

  this.intervalPromise = $interval(this.reload, 5000);
  $scope.$on('$destroy', () => $interval.cancel(this.reload));


}
