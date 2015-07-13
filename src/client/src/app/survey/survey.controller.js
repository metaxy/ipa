'use strict';
export default function SurveyCtrl($stateParams,$rootScope, $http, Shout, ApiUrl, $state) {
  /*this.room = Room.findById({id: $stateParams.roomId}).$promise
    .then((data) => {
      $rootScope.siteTitle = "Umfragen in " + data.name;
      return data;
    });
  */
  this.room = $stateParams.roomId;

  //todo: this.surveys = Room.survey({id: $stateParams.roomId});
  $http.get(ApiUrl+'/r/'+this.room)
  .success((data) => {
      this.surveys = data.surveys;
   })
  .error(() => {
      Shout.error("Could not get surveys");
  });

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
    var survey = {title: title, options: this.options};
		$http.post(ApiUrl+'/r/'+this.room+'/create_survey', survey)
		.success((data) => {
      console.log('Survey created');
      this.update();
    })
		.error((err) => {
      Shout.error('Could not create survey');
    })
		
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
      $http.post(ApiUrl+'/r/'+this.room+'/s/'+survey_id+'/delete')
      .success((data) => {
        console.log('Survey closed');
        this.update();
      })
      .error((err) => {
        Shout.error('Could not delete survey');
      })
  }

  this.close = (survey_id) => {
    $http.post(ApiUrl+'/r/'+this.room+'/s/'+survey_id+'/close')
    .success((data) => {
      console.log('Survey closed');
      this.update();
    })
    .error((err) => {
      Shout.error('Could not delete survey');
    })
  }

  this.update = () => {
    //todo: Room.survey({id: $stateParams.roomId}).$promise.then((data) => this.surveys = data);
    $state.go($state.current, {}, {reload: true});
  }
}
