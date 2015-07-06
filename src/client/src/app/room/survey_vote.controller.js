'use strict';
export default function SurveyVoteCtrl(Survey, $stateParams, Account, $rootScope, Shout) {
  $rootScope.siteTitle = "Umfrage";
  this.survey = Survey.findById({id: $stateParams.surveyId});
  this.options = Survey.surveyOptions({id: $stateParams.surveyId});
  
  this.vote = (survey_option_id) => {
    Account.vote_survey({survey_option_id: survey_option_id}).$promise
      .then(
        (data) => Shout.success("Stimme abgegeben"), 
        (err) => Shout.error("Stimme bereits abgegen")
      );
  }
}