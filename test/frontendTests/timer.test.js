// Import the necessary functions and modules for testing
const { updateTimer, stop_timer, start_timer, set_timer } = require('../../code/frontend/js/timer');
if (typeof TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = require('util');
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><html><body><div id="timer"></div></body></html>');


describe('updateTimer', () => {

  beforeAll(() => {
    dom.window.document.getElementById('timer').innerText = '00:00';
  });
  // Test case 1: When seconds is greater than 0
  it('should decrement seconds and update timer display', () => {
    // Set up initial values
    const time = { minutes: 5, seconds: 10 };
    // Call the function
    updateTimer(time, dom.window.document.getElementById('timer'));

    // Assert the expected results
    expect(time.minutes).toBe(5);
    expect(time.seconds).toBe(9);
    expect(dom.window.document.getElementById('timer').innerText).toBe('05:09');
  });

  // Test case 2: When seconds is 0
  it('should decrement minutes and set seconds to 59', () => {
    // Set up initial values
    const time = { minutes: 5, seconds: 0 };

    // Call the function
    updateTimer(time, dom.window.document.getElementById('timer'));
    // Assert the expected results
    expect(time.minutes).toBe(4);
    expect(time.seconds).toBe(59);
    expect(dom.window.document.getElementById('timer').innerText).toBe('04:59');
  });

  // Test case 3: When minutes and seconds are both 0
  it('should call stop_timer and update timer display', () => {
    // Set up initial values
    const time = { minutes: 0, seconds: 0 };

    // Call the function
    updateTimer(time, dom.window.document.getElementById('timer'));

    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('00:00');
  });
});

describe('start_timer', () => {
  // Test case 1: When the timer is started
  it('should call updateTimer and setInterval', () => {
    // Set up initial values
    const time = { minutes: 1, seconds: 0 };
    const element = dom.window.document.getElementById('timer');

    // Call the function
    start_timer(time, element);

    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('00:59');
    
  });
});

describe('set_timer', () => {
  // Test case 1: When time_seconds is greater than 60
  it('should set the timer display correctly', () => {
    // Set up initial values
    const time_seconds = 90;
    const element = dom.window.document.getElementById('timer');

    // Call the function
    set_timer(time_seconds, element);

    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('1:30');
  });

  // Test case 2: When time_seconds is less than 60
  it('should set the timer display correctly', () => {
    // Set up initial values
    const time_seconds = 45;
    const element = dom.window.document.getElementById('timer');

    // Call the function
    set_timer(time_seconds, element);

    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('0:45');
  });
});