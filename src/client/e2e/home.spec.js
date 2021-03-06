'use strict';
function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

describe('test the home', function () {
  beforeEach(function () {
    browser.get('#/');
  });


  it('navgiation to home should work', function () {
    browser.findElement(by.css('.button-home')).click();
    expect(browser.getCurrentUrl()).toContain("#/");
  });
  
  it('navgiation to user should work', function () {
    browser.findElement(by.css('.button-user')).click();
    expect(browser.getCurrentUrl()).toContain("/user");
  });
  
  it('navgiation to rights should work', function () {
    browser.findElement(by.css('.button-rights')).click();
    expect(browser.getCurrentUrl()).toContain("/rights");
  });
  
  it('navgiation to rights should work', function () {
    browser.findElement(by.css('.button-surveys')).click();
    expect(browser.getCurrentUrl()).toContain("/survey");
  });
  
  it('should be able to create room', function () {
    browser.findElement(by.model('room_name')).sendKeys(makeid());
    browser.findElement(by.model('room_passkey')).sendKeys(makeid());
    browser.findElement(by.css('.button-createroom')).click();
  });

});
