'use strict';
export default function NavbarCtrl(Account, $state, LfAcl, LoopBackAuth) {
    this.me = Account.findById({id: LoopBackAuth.currentUserId});
    this.logout = () => {
      Account.logout().$promise.then((resp) => {
        LfAcl.setRights([]);
        $state.go('login');
      });
  };
}