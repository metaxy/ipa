'use strict';
export default function MainCtrl($state,$rootScope, Shout, $http, ApiUrl) {
  $rootScope.siteTitle = "Start";

  $http.get(ApiUrl+'/list_rooms')
  .success((data) => {
      this.room_names = data.rooms;
   })
  .error(() => {
      Shout.error("Could not get rooms");
  });

  this.joinRoom = (room_name, room_password) => {
    if(_.isUndefined(room_password)) {
      room_password = "";
    }
    $http.post(ApiUrl+'/r/'+ room_name + '/enter' , {passkey : room_password})
    .success((data) => {
        console.log('Entered Room');
        $state.go('room', {roomId: room_name});
    })
    .error(() => {
        Shout.error("Incorrect Password");
    });
  }

  this.createRoom = (room_name, room_passkey) => {
    $http.post(ApiUrl+'/create_room', {name : room_name, passkey: room_passkey})
      .success((data) => {
        Shout.success('Room created');
        $state.go('room', {roomName: data.name});
      })
      .error((err) => {
        Shout.error('Could not create room');
      });
  }

}

