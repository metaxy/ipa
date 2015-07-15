'use strict';
export default function RightsCtrl($state,$rootScope, Shout, $http, ApiUrl) {
  this.optionalRights = ["create_question", "join_lecture", "vote_tempo", "vote_question", "vote_survey", "manage_lecture", "create_survey", "create_room", "view_tempo", "close_survey", "delete_question", "create_account", "delete_account", "assign_role", "create_role", "edit_role", "delete_role", "list_roles", "list_users"];


  $rootScope.siteTitle = "Rechte";

  $http.get(ApiUrl+'/list_users')
    .success((data) => this.all_users = data.users)
    .error(() => Shout.error("Could not get users"));

  $http.get(ApiUrl+'/list_roles')
    .success((data) => this.all_roles = data.roles)
    .error((err) => Shout.error("Could not get roles"));

  this.createRole = (role_name) => {
    $http.post(ApiUrl+'/create_role', {role : role_name})
      .success((data) => {
        Shout.success('Role created');
      })
      .error((err) => {
        Shout.error('Could not create role');
      });
  }

  this.assignRole = (user_name,role_name) => {
    if(_.isUndefined(role_name)) {
      Shout.error("Error: Choose a rolename");
      return;
    }
    if(_.isUndefined(user_name)) {
      Shout.error("Error: Choose a username");
      return;
    }

    $http.post(ApiUrl+'/assign_role', {name : user_name,role: role_name})
      .success((data) => {
        Shout.success('Role successfully asigned');
      })
      .error((err) => {
        Shout.error(err);
      });
  }

  this.editRole = (role_name,new_list_permission) => {
    if(_.isUndefined(role_name)) {
      Shout.error("Error: Choose a rolename");
      return;
    }
    $http.post(ApiUrl+'/role/'+role_name, new_list_permission)
      .success((data) => {
        Shout.success('Role successfully edited');
      })
      .error((err) => {
        Shout.error(err);
      });
  }

  this.deleteRole = (role_name) => {
    if(_.isUndefined(role_name)) {
      Shout.error("Error: Choose a rolename");
      return;
    }
    $http.post(ApiUrl+'/delete_role', {role : role_name})
      .success((data) => {
        Shout.success('Role successfully deleted');
      })
      .error((err) => {
        Shout.error('There are users assigned to this role - can not delete this role.');
      });

}

    $rootScope.selectedRights = [];
    $rootScope.toggle = function (item, list) {
      var idx = list.indexOf(item);
      if (idx > -1) list.splice(idx, 1);
      else list.push(item);
    };
    $rootScope.exists = function (item, list) {
      return list.indexOf(item) > -1;
    };
}

