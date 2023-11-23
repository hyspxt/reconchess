#!/bin/bash

# Run the backend tests and generate coverage report
docker compose -f ../../code/backend/docker-compose.yml \
		run --rm django sh -c "coverage run manage.py test /backendTests && coverage xml"

# replace the contents of the <sources> tag with the correct paths
sed -i '' '/<sources>/,/<\/sources>/c \
	<sources>\
		<source>test<\/source>\
		<source>code/backend/django<\/source>\
	<\/sources>\
' ../../code/backend/django/coverage.xml

# replace all paths referencing /backendTests/ with bakcendTests/
sed -i '' 's/\/backendTests/backendTests/g' ../../code/backend/django/coverage.xml