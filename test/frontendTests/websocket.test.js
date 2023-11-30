import { createWebsocket } from '../../code/frontend/js/websocket';
import { WebSocket } from 'mock-socket';
import { Chess } from 'chess.js';
import { JSDOM } from 'jsdom';
const dom = new JSDOM('<!DOCTYPE html><html><body><div id="timer"></div></body></html>');

global.WebSocket = WebSocket;

describe('createWebsocket', () => {
  let socket;
  let game;
  

  beforeEach(() => {
    // Create a new WebSocket instance before each test
    game = new Chess();
    socket = createWebsocket(game);
  });

  afterEach(() => {
    // Close the WebSocket connection after each test
    socket.close();
  });

  it('should send start_game message when WebSocket connection is opened', async () => {
    // Mock the WebSocket send method
    socket.send = jest.fn();

    // Trigger the onopen event
    socket.onopen();

    // Expect the send method to be called with the expected payload
    expect(socket.send).toHaveBeenCalledWith(JSON.stringify({ action: 'start_game' }));
  });

  // it('should handle game started message correctly', () => {
  //   // Mock the WebSocket onmessage event
  //   const event = {
  //     data: JSON.stringify({ message: 'game started', time: { minutes: 5, seconds: 0 } })
  //   };
    
  //   socket.onmessage(event, game, dom.window.document.getElementById('timer'));

  //   // Expect the game state to be updated correctly
  //   // expect(game.is_over).toBe(false);
  //   expect(set_timer).toHaveBeenCalledWith({ minutes: 5, seconds: 0 });
  //   expect(start_timer).toHaveBeenCalled();
  //   expect(showSideToMove).toHaveBeenCalled();
  // });

  // // Add more test cases for other message types

  // it('should handle game over message correctly', () => {
  //   // Mock the WebSocket onmessage event
  //   const event = {
  //     data: JSON.stringify({ message: 'game over', reason: 'checkmate' })
  //   };
  //   socket.onmessage(event);

  //   // Expect the game state to be updated correctly
  //   expect(stop_timer).toHaveBeenCalled();
  //   expect(game.is_over).toBe(true);
  //   expect(light).toBe(true);
  // });

  // Add more test cases for other message types
});