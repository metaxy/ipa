'use strict';
export default function SpeedCtrl(Speed) {

	this.chosenSpeed='';

  this.faster = () => {
    Speed.faster();
    this.chosenSpeed = 'Schneller';
  }
  
  this.slower = () => {
    Speed.slower();
    this.chosenSpeed = 'Langsamer';
  }

  this.reset = () => {
  	this.chosenSpeed = '';
  	this.reload();
  }
  
  
}