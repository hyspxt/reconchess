// Import the necessary functions and modules for testing
const { createWebsocket } = require('../../code/frontend/js/websocket');

// Mock the WebSocket object
jest.mock('ws');

describe('createWebsocket', () => {
  let socket;

  beforeEach(() => {
    // Create a new WebSocket instance
    socket = createWebsocket();
  });

  afterEach(() => {
    // Close the WebSocket connection
    socket.close();
  });

  // Test case 1: When the WebSocket connection is opened
  it('should send a start_game message', () => {
    // Mock the WebSocket onopen event
    socket.onopen();

    // Assert the expected results
    expect(socket.send).toHaveBeenCalledWith(JSON.stringify({ action: 'start_game' }));
  });

  // Test case 2: When a game started message is received
  it('should update game state and start the timer', () => {
    // Mock the WebSocket onmessage event with a game started message
    socket.onmessage({ data: JSON.stringify({ message: 'game started', time: 60 }) });

    // Assert the expected results
    expect(game.is_over).toBe(false);
    expect(set_timer).toHaveBeenCalledWith(60);
    expect(start_timer).toHaveBeenCalled();
    expect(showSideToMove).toHaveBeenCalled();
  });

  // Test case 3: When a your turn to sense message is received
  it('should turn on the lights', () => {
    // Mock the WebSocket onmessage event with a your turn to sense message
    socket.onmessage({ data: JSON.stringify({ message: 'your turn to sense' }) });

    // Assert the expected results
    expect(lightsOn).toHaveBeenCalled();
    expect(light).toBe(false);
  });

  // Test case 4: When a your turn to move message is received
  it('should show the side to move', () => {
    // Mock the WebSocket onmessage event with a your turn to move message
    socket.onmessage({ data: JSON.stringify({ message: 'your turn to move' }) });

    // Assert the expected results
    expect(showSideToMove).toHaveBeenCalled();
  });

  // Test case 5: When a game over message is received
  it('should stop the timer and update game state', () => {
    // Mock the WebSocket onmessage event with a game over message
    socket.onmessage({ data: JSON.stringify({ message: 'game over', reason: 'checkmate' }) });

    // Assert the expected results
    expect(stop_timer).toHaveBeenCalled();
    expect(game.is_over).toBe(true);
    expect(light).toBe(true);
  });

  // Add more test cases for other message types as needed
});