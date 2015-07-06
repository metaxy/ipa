'use strict';
export default function SurveyCtrl($stateParams,$rootScope) {
  /*this.room = Room.findById({id: $stateParams.roomId}).$promise
    .then((data) => {
      $rootScope.siteTitle = "Umfragen in " + data.name;
      return data;
    });
  */

  //todo: this.surveys = Room.survey({id: $stateParams.roomId});
  this.options = [];

  this.visible_create_from = false;
  this.startNewSurvey = () => {
    this.visible_create_from = true;
    this.options = [{title: ""}];
  }

  this.newOption = () => {
    this.options.push({title: ""});
  }

  this.newSurvey = (title) => {
    var survey = {title: title};
    /*Room.survey.create({id:$stateParams.roomId}, survey).$promise.then((data) => {
      this.options.forEach((d) => {
        Survey.surveyOptions.create({id: data.id}, d);
      });
      this.update();
      this.visible_create_from = false;
    });*/
  }

  this.delete = (survey_id) => {
   //todo: Survey.deleteById({id: survey_id}).$promise.then(() => this.update());
  }

  this.update = () => {
    //todo: Room.survey({id: $stateParams.roomId}).$promise.then((data) => this.surveys = data);
  }
}
