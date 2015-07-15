'use strict';
export default function SurveyCtrl($stateParams, $rootScope, $scope, $http, ApiUrl) {
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
    if(this.open === true) {
      this.close();
    }
  }

  this.close = (survey_id) => {
    this.open = false;
    $http.post(ApiUrl+'/r/'+this.room+'/s/'+survey_id+'/close')
      .success((data) => Shout.success("Umfrage geschlossen"))
      .error((err) => Shout.error('Konnte Umfrage nicht schließen'))
  }


  this.update = () => {
    $http.get(ApiUrl+'/r/'+$stateParams.roomName)
      .success((data) => {
        for(let survey of data.surveys) {
          console.log(survey.title);
          if(survey.id == $stateParams.surveyId) {
            this.survey = survey;
            this.open = survey.open;
            $rootScope.siteTitle = "Umfrage: " + survey.name;
            this.options = data;
            var data = [];
            for(let option of survey.options) {
              //data.push({label: d.title, value: d.votes, color : this.colors[i]});
            }
            this.data = data;
          }
        }
      });
  }
  this.update();

}
