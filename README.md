# reconchess

**reconchess** is a webapp to play Reconnaissance Blind Chess (RBC) games against the computer or other players.git 

## What is RBC?

RBC is a chess variant designed to spice up the tradional game by adding a certain amount of uncertainty and explicit sensing. These are the fundamental differences:

1. Players cannot explicitly see their opponent's piece in the default configuration.
2. Before making any move, the player whose turn it is performs a _sensing_: selecting a 3x3 area on the chess board to _discover_. The discovered area reveals if any enemy chess piece is in that zone, and by consequence, reveals to the player their position on the board. The opponent remains unaware of where the sensing is performed.
3. When a player captures, they are informed of the actual action, but without specifying which piece has been taken.
4. If a player tries to move a piece diagonally (bishops, for example) but there is an opponent's piece on the path, the capture is made and that piece stops on the square where it took place.
5. If a player attempts to make an illegal move, such as moving a pawn diagonally to an empty square (i.e. without capture), or castling through a piece that is not allowed, they are informed that the move is invalid and their turn ends. Players need to keep attention to that or they'll quickly lose.
6. Castling is always possible, even if a player is technically in check, as they do not have complete information of the pieces position on the board.
7. Players can pass the turn without making a move. Nevertheless, a player can sense and then pass.
8. The 'check' concept is practically nonexistent, as players may not be aware of the positions that would result in a check in a traditional game.
9. A players wins by capturing the enemy king or when the opponent runs out of time.
10. Each player starts with 15 minutes to make their moves (sensing + moving the piece) and gains 5 seconds after their turn.
11. A game is automatically declared a stalemate after 50 turns without a pawn move of capture. Players should consider that this is an actual possible strategy to pursuit.

RBC is a chess variant designed by [Johns Hopkins Applied Physics Laboratory](https://rbc.jhuapl.edu/) (JHU/APL) and most of the resources of the games (e.g., StrangeFishv2) comes from them.

## Built with

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white) ![Channels](https://img.shields.io/badge/Channels-0C2233?logo=django&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Caddy](https://img.shields.io/badge/Caddy-00B4F0?logo=caddy&logoColor=white)

![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)

## Contributing

The design, development and deployment followed agile principles.
- Patrick Alfieri | @hyspxt | patrick.alfieri@studio.unibo.it | PO
- Davide Luccioli | @sgrunf | davide.luccioli@studio.unibo.it | Scrum Master S0/S1/S3/S4 | Backend Developer
- Kaori Jiang | @Kmoon7 | kaori.jiang@studio.unibo.it | Frontend Developer
- Sofia Zanelli | @Sofy_zan | sofia.zanelli3@studio.unibo.it | Frontend Developer
- Giulia Torsani | @giulia-t | giulia.torsani@studio.unibo.it | Scrum Master S2 | Backend-db Developer

## Dependencies

To install the required Python dependencies, you can use a Python virtual environment (```venv```) to isolate project dependencies (recommended!), but it is not strictly required. If you prefer, you may install the dependencies directly into your system Python environment.

To use a virtual environment, run:

```bash
git clone https://github.com/hyspxt/reconchess.git
cd reconchess
python -m venv venv
source venv/bin/activate
```

Then, install the dependencies with:

```bash
pip install -r /code/backend/requirements.txt
```

## Running

Build the containers:

```bash
docker-compose build
```

Apply database migrations:

```bash
docker-compose run --rm django sh -c "python manage.py migrate"    
```

Start all services:

```bash
docker-compose up
```

This will start the server and all of its applications (the dependencies you installed before).

## Caddy Config

To serve the reconchess webapp, we used [Caddy](https://caddyserver.com/) as a web server and reverse proxy. Below is a basic example of a `Caddyfile` configuration to proxy requests to your Django backend running on port 8080.
```caddyfile
localhost:8080 {
  root * /reconchess/code/frontend/
  encode gzip
  file_server {
    index home.html
  }
  tls internal

  handle /api/* {
    reverse_proxy /* https://127.0.0.1:8000
  }

  route /static/* {
    uri strip_prefix /static
    root * /reconchess/code/backend/django/static
    file_server
  }
}
```
Caddy must be first be installed (with `pacman -S caddy` or similar, depending on your distro). Then, a basic Caddyfile config will be created and placed in `/etc/caddy`. You can modify that the given example or however you prefer. 

The webapp will then be available at [http://localhost:8080](http://localhost:8080) by default.

---

> cheers, hys 🎴







