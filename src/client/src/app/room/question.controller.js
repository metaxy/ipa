'use strict';
export default function QuestionCtrl($scope, $stateParams, $interval, $http, ApiUrl, Shout) {

  this.questions = [];
  $http.get(ApiUrl+'/r/'+$stateParams.roomId)
  .success((data) => {
      this.questions = data.questions;
   })
  .error(() => {
      Shout.error("Could not get questions");
  });

  this.my_questions = [];

  this.addQuestion = (text) => {
    $http.post(ApiUrl+'/r/'+$stateParams.roomId+'/create_question', {text: text})
    .success((data) => {
      $http.get(ApiUrl+'/r/'+$stateParams.roomId)
      .success((data) => {
          this.questions = data.questions;
       })
      .error(() => {
          Shout.error("Could not get questions");
      });
    })
    .error((err) => {
      Shout.error('Could not create question');
    })
    // todo:
    /*Room.questions.create({id: $stateParams.roomId}, {text: text}).$promise
    .then((data) => this.questions.push(data));*/
  }

  this.reload = () => {
    // todo:
   /* Room.questions({id: $stateParams.roomId, filter: { order: 'votes DESC'}}).$promise
      .then((data) => this.questions = data);

    Account.voted().$promise
      .then((data) => this.my_questions = data.questions);*/
  }

  this.voted = (question_id) => {
    return _.contains(this.my_questions, question_id);
  }

  this.voteIcon = (question_id) => {
    if(this.voted(question_id)) {
      return "thumbs-up";
    }
    return "thumbs-o-up";
  }

  this.vote = (question_id) => {
    this.my_questions.push(question_id);
   //todo: Account.vote({question_id: question_id});
  }

  this.delete = (question_id) => {
   //todo: Question.deleteById({id: question_id}).$promise.then(() => this.reload());
  }

  this.reload();
  this.intervalPromise = $interval(this.reload, 3000);
  $scope.$on('$destroy', () => $interval.cancel(this.intervalPromise));
}
