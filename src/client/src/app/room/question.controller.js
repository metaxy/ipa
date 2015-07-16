'use strict';
export default function QuestionCtrl($scope, $stateParams, $interval, $http, ApiUrl, Shout) {
  this.questions = [];

  this.reload = () => {
    $http.get(ApiUrl+'/r/'+$stateParams.roomId)
      .success((data) => {
        this.questions = data.questions;
      })
      .error(() => Shout.error("Could not get questions"));
  }
  this.reload();

  this.my_questions = [];

  this.addQuestion = (text) => {
    if(_.isUndefined(text) || text.length == 0) {
      Shout.error('Question cannot be empty');
      return;
    }
    $http.post(ApiUrl+'/r/'+$stateParams.roomId+'/create_question', {text: text})
      .success(() => this.reload())
      .error((err) => Shout.error('Could not create question'))
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
    var i = this.my_questions.indexOf(question_id);
    if(i == -1) {
      this.my_questions.push(question_id);
    } else {
      this.my_questions.splice(i,1);
    }
    $http.post(ApiUrl+'/r/'+$stateParams.roomId+'/q/'+question_id+'/vote')
      .success(() => this.reload())
      .error(() => Shout.error('Could not create question'))
  }

  this.delete = (question_id) => {
    /*
    Routes: /api/r/<room_name>/q/<int:question_id>/delete HTTP method: POST
    Request POST data: None
    Response JSON: {"result":
    */
    $http.post(ApiUrl+'/r/'+$stateParams.roomId+'/q/'+question_id+'/delete')
    .success((data) => {
      for(var i  in this.questions) {
        if(this.questions[i].id == question_id) {
          this.questions.splice(i,1);
        }
      }
    })
    .error((err) => {
      Shout.error('Could not delete question');
    })
  }

  this.intervalPromise = $interval(this.reload, 3000);
  $scope.$on('$destroy', () => $interval.cancel(this.intervalPromise));
}
