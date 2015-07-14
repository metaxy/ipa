'use strict';
import _ from 'lodash';
export default function MainCtrl($state,$rootScope, Shout, $http, ApiUrl) {

  $rootScope.siteTitle = "Start";

  $http.get(ApiUrl+'/list_rooms')
  .success((data) => {
      this.room_names = data.rooms;
   })
  .error(() => {
      Shout.error("Could not get rooms");
  });

  $http.get(ApiUrl+'/list_roles')
  .success((data) => {
      this.all_roles = data.roles;
   })
  .error(() => {
      Shout.error("Could not get roles");
  });
  this.all_rooms = $http.get(ApiUrl+'/list_rooms');
  this.optionalRights = ["create_question", "join_lecture", "vote_tempo", "vote_question", "vote_survey", "manage_lecture", "create_survey", "create_room", "view_tempo", "close_survey", "delete_question", "create_account", "delete_account", "assign_role", "create_role", "edit_role", "delete_role", "list_roles", "list_users"];
  this.all_roles = $http.get(ApiUrl+'/list_roles');
  this.all_users = $http.get(ApiUrl+'/list_users');

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

  this.createRole = (role_name) => {
    $http.post(ApiUrl+'/create_role', {role : role_name})
      .success((data) => {
        console.log('Role created', data);
      })
      .error((err) => {
        Shout.error('Could not create role');
      });
  }

  this.editRole = (role_name) => {
    /*$http.post(ApiUrl+'/role/'+role_name, {perms : })
      .success((data) => {

      })
      .error((err) => {

      });*/
  } 

}
