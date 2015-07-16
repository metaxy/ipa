'use strict';
export default function SurveyCtrl($stateParams,$rootScope, $http, Shout, ApiUrl, $state) {
  this.room = $stateParams.roomName;
  $rootScope.siteTitle = "Umfragen in " + this.room;

  $http.get(ApiUrl+'/r/'+$stateParams.roomName)
    .success((data) => this.surveys = data.surveys)
    .error(() => Shout.error("Konnte die Umfragen nicht laden"));

  this.options = [];

  this.visible_create_from = false;
  this.startNewSurvey = () => {
    this.visible_create_from = true;
    this.options = [""];
  }

  this.newOption = () => {
    this.options.push("");
  }

  this.newSurvey = (title) => {
    var survey = {title: title, options: this.options};
		$http.post(ApiUrl+'/r/'+$stateParams.roomName+'/create_survey', survey)
		.success((data) => {
      Shout.success("Umfrage erstellt");
      this.update();
    })
		.error((err) => {
      Shout.error("Konnte Umfrage nicht erstellen");
    })
  }

  this.delete = (survey_id) => {
    $http.post(ApiUrl+'/r/'+this.room+'/s/'+survey_id+'/delete')
    .success((data) => {
      console.log('Umfrage gelöscht');
      var i = this.surveys.indexOf(survey_id);
      this.surveys.splice(i,1);
    })
    .error((err) => {
      Shout.error('Could not delete survey');
    })
  }

  this.close = (survey_id) => {
    $http.post(ApiUrl+'/r/'+this.room+'/s/'+survey_id+'/close')
      .success((data) => Shout.success("Umfrage geschlossen"))
      .error((err) => Shout.error('Konnte Umfrage nicht schließen'))
  }

  this.update = () => {
    $state.go($state.current, {}, {reload: true});
  }
}
