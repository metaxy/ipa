'use strict';
export default function SurveyVoteCtrl($stateParams, $rootScope, Shout, $http, ApiUrl) {
  $rootScope.siteTitle = "Umfrage";
  $http.get(ApiUrl+'/r/'+$stateParams.roomName)
      .success((data) => {
        for(let survey of data.surveys) {
          if(survey.id == $stateParams.surveyId) {
            console.log(survey);
            this.survey = survey;
          }
        }
      });

  this.vote = (option) => {
    $http.post(ApiUrl + '/r/'+ $stateParams.roomName + '/s/' + $stateParams.surveyId + '/vote', {option: option});
  }
}
