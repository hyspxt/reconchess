var board = null
var game = new Chess()
var fen, promote_to
var socket = createWebsocket();
var piece_theme = 'img/chesspieces/wikipedia/{piece}.png';
var promotion_dialog = $('#promotion-dialog');
var promoting = false;
var light = false
var letters, part2 = null
var comments = ""



function haveEaten(target){
    if(target === 'b'){
        comments = "white has eaten a black piece\n" + comments
    } 
    
    if(target === 'w') {
        comments = "black has eaten a white piece\n" + comments
    }
    document.getElementById("History").innerText = comments;

}

function showSideToMove() {
    if(game.turn() === 'w') {
        comments =  "it's white turn to move\n" + comments;
    } else {
        comments = "it's black turn to move\n" +  comments;
    }

    document.getElementById("History").innerText = comments;
}

function illegalMove(){
    comments = "illegal move\n" +  comments;
    document.getElementById("History").innerText = comments;
}

function onDragStart (source, piece) {
    document.body.style.overflow = 'hidden';
    // do not pick up pieces if the game is over
    if (game.game_over() || game.is_over) return false

    if (piece.search(/^b/) !== -1) return false
    //turn off light
    if (light) {
        lightsOff();
        light = false;
    }
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
        if(light) lightsOff()
        lightsOn()
        config.draggable = false
}

function onDrop (source, target) {
    move_cfg = {
        from: source,
        to: target,
        promotion: 'q'
      };

    var target_piece = game.get(target);

    // check we are not trying to make an illegal pawn move to the 8th or 1st rank,
    // so the promotion dialog doesn't pop up unnecessarily
    var move = game.move(move_cfg);

    // illegal move
    if (move === null) {
        document.body.style.overflow = 'visible';
        config.draggable = true;
        illegalMove();
        return 'snapback'
    } else game.undo(); //move is ok, now we can go ahead and check for promotion

    var source_rank = source.substring(2,1);
    var target_rank = target.substring(2,1);
    var piece = game.get(source).type;

    //change the opacity of the squares
    if (piece.search(/^w/)) {
        var squareSource = $('#myBoard .square-' + source);
        var squareTarget = $('#myBoard .square-' + target);
        squareTarget.css('opacity', 1);
        squareTarget.css('filter', 'none');
        squareSource.css('opacity', 0.4);
        squareSource.css('filter', 'grayscale(50%) blur(2px) brightness(0.8)');
    }

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

function onSnapEnd () {
    if (promoting) return;
    updateBoard(board);
}

function getImgSrc(piece) {
    return piece_theme.replace('{piece}', game.turn() + piece.toLocaleUpperCase());
}

function updateBoard(board) {
    board.position(game.fen(), false);
    promoting = false;
    config.draggable = false;
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
    if (move === null){
        config.draggable = true;
        illegalMove();
        return 'snapback';
    }
    else {
        //convert move to UCI format
        move = move_cfg.from + move_cfg.to
        //add promotion to the move only if it actually includes a promotion
        if (promotion)
            move += move_cfg.promotion;
        //send the chosen move to the backend
        socket.send(JSON.stringify({ action: 'move', move: move}));
        console.log('you moved: ' + move_cfg.from + move_cfg.to);
        config.draggable = false;
    }

}


function lightsOn(){
    window.addEventListener("click", function(event) {
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
            while (i < 3){
                j = 0;
                while (j < 3){
                    var square = $('#myBoard .square-' + letters[j] + part2);
                    square.css('opacity', 1);
                    square.css('filter', 'none');
                    
                    var pieceImage= square.find('img[data-piece]');
                    pieceImage.css('opacity', 1);
                    j++;
                }
                part2++;
                i++;
            }
            config.draggable = true;
            light = true;
        }
    }, {passive:false});
}

function lightsOff(){
    var i = 0;
    part2 = part2 - 3;
    while (i < 3){
        j = 0; 
        while (j < 3){
            var square = $('#myBoard .square-' + letters[j] + part2);
            console.log("output: " + letters[j] + part2);
            square.css({
                'opacity': 0.4,
                'filter': 'grayscale(50%) blur(2px) brightness(0.8)' 
            });

            var piece = square.find('img[data-piece]');
            if (piece.length > 0) {
                var dataPieceValue = piece.attr('data-piece');
                
                //check for white pieces
                if (dataPieceValue && dataPieceValue.startsWith('w')) {
                    console.log("output: " + square);
                    square.css({
                        'opacity': 1,
                        'filter': 'none'
                    });
                }else piece.css('opacity', 0); //opacity for black pieces
            }
            j++;
        }
        part2++;
        i++;
    }
}

function resign(rematch = false) {
    config.draggable = false;
    if (light){
        light = false;
        lightsOff();
    }
    //reset fog
    var squares = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 'e1', 'e2', 'f1', 'f2', 'g1', 'g2', 'h1', 'h2'];

    $('#myBoard .square-55d63').css('opacity', 0.4)
    $('#myBoard .square-55d63').css('filter', 'grayscale(50%) blur(2px) brightness(0.8)')

    squares.forEach(function(square){
        var squareTarget = $('#myBoard .square-' + square);
        squareTarget.css('opacity', 1);
        squareTarget.css('filter', 'none');
    });
    console.log(rematch);
    game.reset();
    board.start();
    socket.send(JSON.stringify({ action: 'resign', rematch: rematch }));
    
}

var config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
}

board = Chessboard('myBoard', config)

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