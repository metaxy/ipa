'use strict';
import _ from 'lodash';
export default function MainCtrl($state,$rootScope, Shout, $http, ApiUrl) {
  //Room.find().$promise.then((data) => {this.room_names =  _.pluck(data, 'name');});

  // RÄUME SETZEN BEI VERANSTALTUNG BEITRETEN
 $http.get(ApiUrl+'/list_rooms')
  .success((data) => {
      this.room_names = data.rooms;
   })
  .error(() => {
      Shout.error("Could not get rooms");
  });

  $rootScope.siteTitle = "Start";

  this.joinRoom = (room_name, room_password) => {
    $http.post(ApiUrl+'/r/'+ room_name + '/enter' , {passkey : room_password})
    .success((data) => {
        console.log('Entered Room');
        $state.go('room', {roomId: room_name});
    })
    .error(() => {
        Shout.error("Incorrect Password");
    });
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

  this.createRoom = (room_name, room_passkey) => {
    $http.post(ApiUrl+'/create_room', {name : room_name, passkey: room_passkey})
      .success((data) => {
        console.log('Room created', data);
        $state.go('room', {roomId: data.name});
      })
      .error((err) => {
        Shout.error('Could not create room');
      });
  }

  this.createAccount = (account_name, account_password) => {
    $http.post(ApiUrl+'/create_account', {name : account_name, password: account_password})
      .success((data) => {
        console.log('Account created', data);
        $state.go('user');
      })
      .error((err) => {
        Shout.error('Could not create account');
      });
  }

}
