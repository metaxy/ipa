'use strict';

describe('test the home', function () {
  beforeEach(function () {
    browser.get('#/surveys');
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

});
