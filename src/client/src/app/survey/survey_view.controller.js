'use strict';
export default function SurveyCtrl($stateParams, $rootScope, $scope) {
  this.open = false;
  this.data = [];
  this.opt = {thickness: 20};
  this.colors = [
  '#56E289',
  '#56AEE2',
  '#ABDE55',
  '#8A56E2',
  '#E25668',
  '#CF56E2',
  '#E256AE',
  '#5668E2',
  '#E28956',
  '#E0CD55',
  '#56E2CF',
  '#68E256'
  ];
  this.buttonIcon = () => {
    if(this.open == true) {
      return "pause";
    }
    return "play";
  }
  this.toggleSurvey = () => {
    this.survey.open = !this.survey.open;
    this.open = !this.open;
    //todo: Survey.upsert(this.survey);
  }

  this.update = () => {
    /*Survey.findById({id: $stateParams.surveyId}).$promise.then((data) => {
      this.survey = data;
      this.open = data.open;
      $rootScope.siteTitle = "Umfrage: " + data.title;
    });
    Survey.surveyOptions({id: $stateParams.surveyId}).$promise.then((data) => {
      this.options = data;
      var data = [];
      this.options.forEach((d,i) => {
        console.log(this.colors[i]);
        data.push({label: d.title, value: d.votes, color : this.colors[i]});
      });
      this.data = data;

    });*/
  }
  this.update();


}
