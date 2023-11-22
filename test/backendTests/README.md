## Description
Cartella contenente i test di backend del progetto.

i test sono stati scritti utilizzando il framework di testing di Django.

## Prerequisiti
per eseguire i test è necessario che il container docker sia in funzione.

## Esecuzione
per eseguire tutti i test: 

docker compose exec django python manage.py test /backendTests

per eseguire un singolo test:

docker compose exec django python manage.py test nome_modulo

per ottenere coverage dei test:

docker compose run --rm django sh -c "coverage run manage.py test /backendTests && coverage xml"
e modificare il file coverage.xml in modo che il tag "sources" sia:
	<sources>
		<source>test</source>
		<source>code/backend/django</source>
	</sources>

