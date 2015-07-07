'use strict';
export default function LoginCtrl(LfAcl, $state, ApiUrl, Shout, $http) {

  this.login = (username, password) => {
    $http.post(ApiUrl+'/login', {uid : username, password: password})
      .success(() => {
         $http.get(ApiUrl+'/list_permissions')
         .success((data) => {
           LfAcl.setRights(data);
           $state.go('home');
         })
         .error(() => {
            LfAcl.setRights([]);
            Shout.error("Could not get permissions");
          }
         );
      })
      .error((err) => {
        LfAcl.setRights([]);
        Shout.error(err);
      });
  }


}
