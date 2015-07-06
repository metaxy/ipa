'use strict';
export default function LoginCtrl(LfAcl, $state, ApiUrl, Shout, $http) {
  
  this.login = (username, password) => {
    $http.post(ApiUrl+'/login', {uid : username, password: password})
      .success(() => {
         $http.get(ApiUrl+'/list_permissions')
         .success((data) => {
           LfAcl.setRights(LfAcl.student);
           $state.go('home');
         })
         .error(() => {
            LfAcl.setRights(LfAcl.allRights);
            $state.go('home');
          }
         );
      })
      .error((err) => {
        LfAcl.setRights([]);
        Shout.error(err);
      });
  }
  
  
}