'use strict';
export default function QuestionCtrl($scope, $stateParams, Room, $interval, Account, Question) {
  this.questions = [];
  this.my_questions = [];

  this.addQuestion = (text) => {
    Room.questions.create({id: $stateParams.roomId}, {text: text}).$promise
    .then((data) => this.questions.push(data));
  }

  this.reload = () => {
    Room.questions({id: $stateParams.roomId, filter: { order: 'votes DESC'}}).$promise
      .then((data) => this.questions = data);

    Account.voted().$promise
      .then((data) => this.my_questions = data.questions);
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
    Account.vote({question_id: question_id});
  }

  this.delete = (question_id) => {
    Question.deleteById({id: question_id})
      .$promise.then(() => this.reload());
  }

  this.reload();
  this.intervalPromise = $interval(this.reload, 3000);
  $scope.$on('$destroy', () => $interval.cancel(this.intervalPromise));
}
