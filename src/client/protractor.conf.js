'use strict';
exports.config = {
  multiCapabilities: [
    {
      browserName : 'firefox'
    }
  ],


  // Spec patterns are relative to the current working directly when
  // protractor is called.
  specs: ['e2e/**/*.js'],

  baseUrl : "http://localhost:3000/",

  // Options to be passed to Jasmine-node.
  jasmineNodeOpts: {
    showColors: true,
    defaultTimeoutInterval: 30000
  },

  onPrepare: function() {
    browser.get('#/login');

    browser.findElement(by.model('username')).sendKeys('admin');
    browser.findElement(by.model('password')).sendKeys('admin');
    browser.findElement(by.css('.md-button')).click();

    // Login takes some time, so wait until it's done.
    // For the test app's login, we know it's done when it redirects to
    // index.html.
    return browser.wait(function() {
      return browser.getCurrentUrl().then(function(url) {
        return true;
      });
    }, 10000);
  }
};
