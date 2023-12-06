import { createWebsocket } from './websocket.js'
import { valid_moves, player_color } from './websocket.js'

var board = null
var game = new Chess()
var fen, promote_to
var socket = createWebsocket(game, document.getElementById('player_timer'), document.getElementById('opponent_timer'))
var piece_theme = 'img/chesspieces/wikipedia/{piece}.png'
var promotion_dialog = $('#promotion-dialog')
var promoting = false
var light = false
var letters, part2 = null
var comments = ""
var pass = false
var color = 'w'

//activates when the user switches tabs
document.addEventListener("visibilitychange", () => {
    console.log('visibility changed' + document.visibilityState)
    //when the tab is active send a request for the timers to the backend
    if (document.visibilityState === 'visible')
        console.log('send request for timers')
        socket.send(JSON.stringify({ action: 'get_active_timer' }));
});

var config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
}

export function haveEaten(target) {
    if (target === 'b') {
        comments = "white has eaten a black piece\n" + comments
    }
    if (target === 'w') {
        comments = "black has eaten a white piece\n" + comments
    }
    document.getElementById("History").innerText = comments;
}

export function showSideToMove(game_turn) {
    if (pass == false) {
        if (game_turn === player_color) {
            comments = "it's your turn to move\n" + comments;
        } else {
            comments = "opponent's turn\n" + comments;
        }
        document.getElementById("History").innerText = comments;
    }
    else pass = false;
}

export function illegalMove() {
    comments = "illegal move\n" + comments;
    document.getElementById("History").innerText = comments;
}

export function showSense() {
    comments = "it's your turn to sense\n" + comments;
    document.getElementById("History").innerText = comments;
}

export function youPassed() {
    if (game.turn() === 'w') {
        comments = "you passed\n" + comments;
        document.getElementById("History").innerText = comments;
    }
}

export function showGameOver(reason, winner) {
    let result = winner ? 'White won, ' : (winner !== 'None' ? 'black won, ' : 'Draw')
    comments = result + reason + "\n" + comments
    document.getElementById("History").innerText = comments;
}

export function onDragStart(source, piece) {
    document.body.style.overflow = 'hidden';
    // do not pick up pieces if the game is over
    if (game.game_over() || game.is_over) return false

    if (piece.search(/^b/) !== -1) return false
    //turn off light
    if (light) lightsOff();
}

//update the game board with the move made by the opponent
export function makeOpponentMove(board_conf) {
    //load the board fen sent by the backend
    game.load(board_conf);
    //updte the board shown to the user
    board.position(game.fen());

}

//taken fron https://github.com/jhlywa/chess.js/issues/382
export function passTurn() {
    pass = true;
    youPassed();
    console.log('pass turn')
    console.log(game.WHITE)
    //get the current fen and split it in tokens
    let tokens = game.fen().split(/\s/)
    //change the turn token
    tokens[1] = game.turn() == game.WHITE ? game.BLACK : game.WHITE
    tokens[3] = '-' // reset the en passant square 
    game.load(tokens.join(' '))
    //TODO: change this to check for the player's turn not just white
    if (game.turn() === game.BLACK) {
        socket.send(JSON.stringify({ action: 'pass' }));
        console.log('you passed');
    }
    if (light) lightsOff()
    lightsOn()
}

export function onDrop(source, target) {
    document.body.style.overflow = 'visible';
    let move_cfg = {
        from: source,
        to: target,
        promotion: 'q'
    };


    // check we are not trying to make an illegal pawn move to the 8th or 1st rank,
    // so the promotion dialog doesn't pop up unnecessarily
    if (!valid_moves.some(move => move.startsWith(source + target))) {
        document.body.style.overflow = 'visible';
        illegalMove();
        config.draggable = true;
        return 'snapback';
    }

    var source_rank = source.substring(2, 1);
    var target_rank = target.substring(2, 1);
    var source_column = source.substring(0, 1);
    var target_column = target.substring(0, 1);
    console.log('source column: ' + source_column);
    console.log('target column: ' + target_column);
    var piece = game.get(source).type;
    var target_type = game.get(target);
    console.log(target_type);

    //change the opacity of the squares
    if (piece.search(/^w/)) {
        var squareSource = $('#myBoard .square-' + source);
        var squareTarget = $('#myBoard .square-' + target);
        squareTarget.css('opacity', 1);
        squareTarget.css('filter', 'none');
        squareSource.css('opacity', 0.4);
        squareSource.css('filter', 'grayscale(50%) blur(2px) brightness(0.8)');
    }

    if (piece === 'p' &&
        (
        (source_rank === '7' && target_rank === '8') ||
        (source_rank === '2' && target_rank === '1')
        ) &&
        (source_column === target_column ? target_type === null : true) &&
        (source_column != target_column ? target_type !== null : true)
    ) {
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
            close: () => onDialogClose(move_cfg),
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
    makeMove(game, move_cfg, false);
}

export function onSnapEnd() {
    if (promoting) return;
    updateBoard(board);
}

export function getImgSrc(piece) {
    return piece_theme.replace('{piece}', game.turn() + piece.toLocaleUpperCase());
}

export function updateBoard(board) {
    board.position(game.fen(), false);
    promoting = false;
}

var onDialogClose = function (move_cfg) {
    console.log('promote toooooo' + promote_to);
    move_cfg.promotion = promote_to;
    makeMove(game, move_cfg, true);
}

export function makeMove(game, move_cfg, promotion = false) {
    //see if the move is legal
    //convert move to UCI format
    console.log(config);

    console.log(move_cfg.to);
    console.log(move_cfg.from);
    var move = move_cfg.from + move_cfg.to;
    //add promotion to the move only if it actually includes a promotion
    if (promotion)
        move += move_cfg.promotion;

    console.log(move);

    // illegal move
    if (!(valid_moves.includes(move))) {
        illegalMove();
        config.draggable = true;
        return 'snapback';
    }
    else {
        //make the move
        var piece = game.get(move_cfg.from);
        game.remove(move_cfg.from);
        game.put(piece, move_cfg.to);
        //send the chosen move to the backend
        socket.send(JSON.stringify({ action: 'move', move: move }));
        console.log('you moved: ' + move_cfg.from + move_cfg.to);
        config.draggable = false;
    }
}

export function lightsOn() {
    config.draggable = false;
    window.addEventListener("click", function (event) {
        if ((event.target.classList.contains("square-55d63")) && (light == false)) {
            var position = event.target.getAttribute("data-square");
            var part1 = position.substring(0, 1);
            var part1Ascii = part1.charCodeAt(0);
            var prec
            var suc = String.fromCharCode(part1Ascii + 1);

            if (part1 != 'a') prec = String.fromCharCode(part1Ascii - 1);
            else prec = null;

            letters = [prec, part1, suc];
            part2 = position.substring(position.length - 1);
            //turn on light
            var i = 0;
            part2--;
            while (i < 3) {
                var j = 0;
                while (j < 3) {
                    var square = $('#myBoard .square-' + letters[j] + part2);
                    square.css('opacity', 1);
                    square.css('filter', 'none');

                    var pieceImage = square.find('img[data-piece]');
                    pieceImage.css('opacity', 1);
                    j++;
                }
                part2++;
                i++;
            }
            config.draggable = true;
            light = true;
            //send the sense message to the backend
            socket.send(JSON.stringify({ action: 'sense', sense: position }));
        }
    }, { passive: false });
}

export function lightsOff() {
    var i = 0;
    var letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
    while (i < 8) {
        var y = 0;
        while (y < 8) {
            var square = $('#myBoard .square-' + letters[y] + (i + 1));
            square.css({
                'opacity': 0.4,
                'filter': 'grayscale(50%) blur(2px) brightness(0.8)'
            });
            var piece = square.find('img[data-piece]');
            if (piece.length > 0) {
                var dataPieceValue = piece.attr('data-piece');

                //check for white pieces
                if (dataPieceValue && dataPieceValue.startsWith(color)) {
                    square.css({
                        'opacity': 1,
                        'filter': 'none'
                    });
                } else piece.css('opacity', 0); //opacity for black pieces
            }
            y++;
        }
        i++;
    }
    light = false;
}

export function resign(rematch = false) {
    
    config.draggable = false;
    console.log('light ' + light);
    if (light && !game.is_over) lightsOff();
    //reset fog
    var squares = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 'e1', 'e2', 'f1', 'f2', 'g1', 'g2', 'h1', 'h2'];

    $('#myBoard .square-55d63').css('opacity', 0.4)
    $('#myBoard .square-55d63').css('filter', 'grayscale(50%) blur(2px) brightness(0.8)')

    squares.forEach(function (square) {
        var squareTarget = $('#myBoard .square-' + square);
        squareTarget.css('opacity', 1);
        squareTarget.css('filter', 'none');
    });
    game.reset();
    board.start();
    //avoid trying to send the message while the page is loading
    if (socket.readyState == WebSocket.OPEN)
        socket.send(JSON.stringify({ action: 'resign', rematch: rematch }));
}

export function flipSide(){
    game.flip();
    color = 'b';
}

board = Chessboard('myBoard', config)

$("#promote-to").selectable({
    stop: function () {
        $(".ui-selected", this).each(function () {
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
