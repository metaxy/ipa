'use strict';
export default function SurveyVoteCtrl($stateParams, $rootScope, Shout) {
  console.log('$stateParams ', $stateParams);
  $rootScope.siteTitle = "Umfrage";
  this.survey = $stateParams.surveyId;

  this.vote = (survey_option_id) => {
  }
}
