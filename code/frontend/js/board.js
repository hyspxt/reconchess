var board = null
var game = new Chess()
var whiteSquareGrey = '#A3CEF1'
var blackSquareGrey = '#274C77'
var fen, piece_theme, promote_to, promoting, promotion_dialog;
var socket = createWebsocket();
piece_theme = 'img/chesspieces/wikipedia/{piece}.png';
promotion_dialog = $('#promotion-dialog');
promoting = false;

function removeGreySquares () {
    $('#myBoard .square-55d63').css('background', '')
}

function greySquare (square) {
    var $square = $('#myBoard .square-' + square)

    var background = whiteSquareGrey
    if ($square.hasClass('black-3c85d')) {
        background = blackSquareGrey
    }

    $square.css('background', background)
}

function onDragStart (source, piece) {
    document.body.style.overflow = 'hidden';
    // do not pick up pieces if the game is over
    if (game.game_over() || game.is_over) return false

    if (piece.search(/^b/) !== -1) return fa
}

//TODO: if this isn't needed remove it
function makeRandomMove () {
    var possibleMoves = game.moves()
  
    // game over
    if (possibleMoves.length === 0) return
  
    var randomIdx = Math.floor(Math.random() * possibleMoves.length)
    game.move(possibleMoves[randomIdx])
    board.position(game.fen())
}  
  
//update the game board with the move made by the opponent
function makeOpponentMove(board_conf) {
    //load the board fen sent by the backend
    game.load(board_conf);
    //updte the board shown to the user
    board.position(game.fen());
}

//taken fron https://github.com/jhlywa/chess.js/issues/382
function passTurn() {
    //get the current fen and split it in tokens
    let tokens = game.fen().split(/\s/)
    //change the turn token
    tokens[1] = game.turn() == game.WHITE ? game.BLACK : game.WHITE
    tokens[3] = '-' // reset the en passant square 
    game.load(tokens.join(' '))
    if (game.turn() == game.WHITE)
        socket.send(JSON.stringify({ action: 'move', move: 'pass'  }));
}

function onDrop (source, target) {
    removeGreySquares()
    move_cfg = {
        from: source,
        to: target,
        promotion: 'q'
      };

      // check we are not trying to make an illegal pawn move to the 8th or 1st rank,
      // so the promotion dialog doesn't pop up unnecessarily
      // e.g. (p)d7-f8
      var move = game.move(move_cfg);

    // illegal move
    if (move === null) {
        //document.body.style.overflow = 'visible';
        return 'snapback'
    } else {
        game.undo(); //move is ok, now we can go ahead and check for promotion
    }

    var source_rank = source.substring(2,1);
    var target_rank = target.substring(2,1);
    var piece = game.get(source).type;

    if (piece === 'p' && ((source_rank === '7' && target_rank === '8') || (source_rank === '2' && target_rank === '1'))) {
        promoting = true;

        // get piece images
        $('.promotion-piece-q').attr('src', getImgSrc('q'));
        $('.promotion-piece-r').attr('src', getImgSrc('r'));
        $('.promotion-piece-n').attr('src', getImgSrc('n'));
        $('.promotion-piece-b').attr('src', getImgSrc('b'));
        
        //show the select piece to promote to dialog
        promotion_dialog.dialog({
            modal: true,
            height: 46,
            width: 184,
            resizable: true,
            draggable: false,
            close: onDialogClose,
            closeOnEscape: false,
            dialogClass: 'noTitleStuff'
        }).dialog('widget').position({
            of: $('#myBoard'),
            my: 'middle middle',
            at: 'middle middle',
        });
        
        //the actual move is made after the piece to promote to
        //has been selected, in the stop event of the promotion piece selectable
        return;
    }
    makeMove(game, move_cfg);
}

function onMouseoverSquare (square, piece) {
    // get list of possible moves for this square
    var moves = game.moves({
        square: square,
        verbose: true
    })

    // exit if there are no moves available for this square
    if (moves.length === 0 || game.is_over) return

    // highlight the square they moused over
    greySquare(square)

    // highlight the possible squares for this piece
    for (var i = 0; i < moves.length; i++) {
        greySquare(moves[i].to)
    }
}

function onMouseoutSquare (square, piece) {
    removeGreySquares()
}

function onSnapEnd () {
    if (promoting) return;
    updateBoard(board);
    document.body.style.overflow = 'visible';
    board.position(game.fen())
}

function getImgSrc(piece) {
    return piece_theme.replace('{piece}', game.turn() + piece.toLocaleUpperCase());
  }

  function updateBoard(board) {
    board.position(game.fen(), false);
    promoting = false;
  }

  var onDialogClose = function() {
    console.log(promote_to);
    move_cfg.promotion = promote_to;
    makeMove(game, move_cfg, true);
  }

function makeMove(game, config, promotion=false) {
    // see if the move is legal
    var move = game.move(config);
    // illegal move
    if (move === null)
        return 'snapback';
    else {
        //convert move to UCI format
        move = move_cfg.from + move_cfg.to
        //add promotion to the move only if it actually includes a promotion
        if (promotion)
            move += move_cfg.promotion;
        //send the chosen move to the backend
        socket.send(JSON.stringify({ action: 'move', move: move}));
        console.log('you moved: ' + move_cfg.from + move_cfg.to);
    }

  }

var config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onMouseoutSquare: onMouseoutSquare,
    onMouseoverSquare: onMouseoverSquare,
    onSnapEnd: onSnapEnd
}
board = Chessboard('myBoard', config)

function resign(rematch = false) {
    console.log(rematch)
    game.reset();
    board.start();
    socket.send(JSON.stringify({ action: 'resign', rematch: rematch }));
}

$("#promote-to").selectable({
    stop: function() {
      $( ".ui-selected", this ).each(function() {
        var selectable = $('#promote-to li');
        var index = selectable.index(this);
        if (index > -1) {
          var promote_to_html = selectable[index].innerHTML;
          var span = $('<div>' + promote_to_html + '</div>').find('span');
          promote_to = span[0].innerHTML;
        }
        promotion_dialog.dialog('close');
        $('.ui-selectee').removeClass('ui-selected');
        updateBoard(board);
      });
    }
  });


function undoMove(){
    game.undo(),
    game.undo(),
    game.load(game.fen()),
    board.position(game.fen())
}