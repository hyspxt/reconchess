import { updateTimer, start_timer, set_timer } from '../../code/frontend/js/timer';
import { JSDOM } from 'jsdom';
const dom = new JSDOM('<!DOCTYPE html><html><body><div id="timer"></div></body></html>');


describe('updateTimer', () => {

  beforeAll(() => {
    dom.window.document.getElementById('timer').innerText = '00:00';
  });
  // Test case 1: When seconds is greater than 0
  it('should decrement seconds and update timer display', () => {
    // Set up initial values
    const time = 121;
    // Call the function
    updateTimer(time, dom.window.document.getElementById('timer'));

    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('02:00');
  });

  // Test case 2: When seconds is 0
  it('should decrement minutes and set seconds to 59', () => {
    // Set up initial values
    const time = 120

    // Call the function
    updateTimer(time, dom.window.document.getElementById('timer'));
    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('01:59');
  });

  // Test case 3: When minutes and seconds are both 0
  it('should call stop_timer and update timer display', () => {
    // Set up initial values
    const time = 0
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
    const time = 60;
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
    const time = 110
    const element = dom.window.document.getElementById('timer');

    // Call the function
    set_timer(time, element);

    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('01:50');
  });

  // Test case 2: When time_seconds is less than 60
  it('should set the timer display correctly', () => {
    // Set up initial values
    const time = 150
    const element = dom.window.document.getElementById('timer');

    // Call the function
    set_timer(time, element);

    // Assert the expected results
    expect(dom.window.document.getElementById('timer').innerText).toBe('02:30');
  });
});