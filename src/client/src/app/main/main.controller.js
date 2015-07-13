'use strict';
import _ from 'lodash';
export default function MainCtrl($state,$rootScope, Shout, $http, ApiUrl) {
  //Room.find().$promise.then((data) => {this.room_names =  _.pluck(data, 'name');});
  //this.my_rooms = Account.rooms({id:LoopBackAuth.currentUserId});
  $rootScope.siteTitle = "Start";

  this.joinRoom = (room_name, room_password) => {

    /*Account.joinRoom({room: room_name, code: room_password})
    .$promise.then(
      (data) => {
        $state.go('room', {roomId: data.data});
      },
      (err) => {
        Shout.error("Falsches Passwort");
      }
    );
    */
  }

  this.createRoom = (room_name, room_password) => {
    $http.post(ApiUrl+'/create_room', {name : room_name, password: room_password})
      .success((data) => {
        $state.go('room', {roomName: data.name});
      })
      .error((err) => {
        Shout.error(err);
      });
  }

}
