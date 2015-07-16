'use strict';
export default function RoomCtrl($scope, $stateParams, $interval, $rootScope) {
  $rootScope.siteTitle = $stateParams.roomId;
}
