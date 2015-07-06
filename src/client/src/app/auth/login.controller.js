'use strict';
export default function LoginCtrl(LfAcl, $state, Account, Shout) {
  this.processLogin = (resp) => {
    Account.roles({'user_id': resp.user.id})
      .$promise.then((resp) => {
        LfAcl.setRights(resp.roles);
        $state.go('home');
    });
  }
  
  this.login = (username, password) => {
    Account.login({rememberMe: true},{email: username, password: password}
    )
    .$promise.then(
      this.processLogin,
      (err) => {
        Account.create({email: username, password: password}).$promise
        .then(
          (ok) => {
            Account.login({rememberMe: true},{email: username, password: password}).$promise.then(
              this.processLogin,
              (err) => Shout.vError(err)
            );
          },
          (err) => {
            Shout.vError(err);
          }
       );
      }
    );
  }
  
  
}