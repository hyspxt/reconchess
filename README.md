# ReconnassainceBlindChess

## Contributing

T8 Silver Bullets
- Patrick Alfieri | @hyspxt | patrick.alfieri@studio.unibo.it | Product Owner
- Davide Luccioli | @sgrunf | davide.luccioli@studio.unibo.it | Scrum Master S0/S1/S3/S4 | Backend Developer
- Kaori Jiang | @Kmoon7 | kaori.jiang@studio.unibo.it | Frontend Developer
- Sofia Zanelli | @Sofy_zan | sofia.zanelli3@studio.unibo.it | Frontend Developer
- Giulia Torsani | @giulia-t | giulia.torsani@studio.unibo.it | Scrum Master S2 | Backend-db Developer

## Description
Questa repository contiene il progetto di Ingegneria del Software, CdL Informatica 23/24. 
Si tratta di un'applicazione web che permette di giocare alla variante Reconnassaince Blind Chess degli scacchi eterodossi in modalitá HumanVsComputer, a livelli di difficoltá crescenti.  
**Reconnassaince Blind Chess** é una variante degli scacchi (piú precisamente, una famiglia di varianti) formulata come progetto di ricerca e sviluppo al Johns Hopkins Applied Physics Laboratory (JHU/APL). Sebbene la challenge scientifica in sé si concentri sullo sviluppo di bot, il progetto vuole rappresentare un'implementazione classica e giocabile della variante.

RBC aggiunge i seguenti elementi agli scacchi classici:
- Sensing.
- Informazione incompleta iniziale.
- Scelte su condizioni di insicurezza.

ReconChess é un paradigma e banco di prova per capire e sperimentare il decision making autonomo strategico attraverso una serie di iterazioni di sensing.

## Dependencies, Running
L'applicazione richiede le seguenti dipendenze:

```bash
asgiref==3.7.2
Django==4.2.7
packaging==23.2
psycopg2-binary==2.9.9
sqlparse==0.4.4
daphne==4.0.0
channels==4.0.0
reconchess==1.6.9
coverage==7.3.2
click==8.1.7
tqdm==4.66.1
numpy==1.26.2
google-api-python-client==2.24.0
```

Esse vengono installate automaticamente, ma é anche possibile utilizzare il comando:
```bash
pip install -r /code/backend/requirements.txt
```

L'applicazione é attualmente accessibile su -> [silverbullets.rocks](url)

## Info
### Communicating
Come sistema di comunicazione interno al team, abbiamo preferito garantire la totale proprietá e controllo dei nostri dati utilizzando il servizio decentralizzato **Matrix**, completamente self-hostato attraverso una droplet dedicata DigitalOcean e un dominio apposito. Il servizio é accessibile mediante il client **Element**, che fornisce un interfaccia intuitiva e funzionale per le comunicazioni del gruppo. Il server é organizzato in stanze, in modo da poter facilitare e organizzare i topic di cui si parla.

### Agile/Scrum 
Il team ha sviluppato il progetto seguento la metodologia e i principi agili, in particolare attraverso gli eventi Scrum quali Sprint Review, Sprint Planning, Sprint Retrospective. Piuttosto che seguire la filosofia Daily Scrum (uno Scrum Meeting al giorno), si é optato per Weekly Scrum in modo da venire incontro agli impegni individuali di tutti i membri.

Durante il Sprint Planning, si discute in base agli obiettivi dello sprint corrente e si dividono i compiti tra i membri del team in base alle competenze e alla disponibilità di ciascuno. Cerchiamo di bilanciare il carico di lavoro in modo equo.
La Sprint Review è un evento per riflettere sul lavoro svolto durante lo sprint.
Dopo ogni sprint, teniamo una Sprint Retrospective per discutere delle buone pratiche adottate, quelle da migliorare e quelle da rimuovere. Questo ci aiuta a diventare un team più efficace.







