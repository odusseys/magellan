#!/bin/bash

CONTAINER=postgres-test

docker pull postgres/10
docker run -p 5432:5432 --name $CONTAINER -e POSTGRES_PASSWORD=test -d postgres

DATABASE_URL=postgresql://postgres:test@localhost:5432/users
DATABASE_USER=postgres
DATABASE_PASSWORD=test
DATABASE_HOST=localhost

# wait for db to be up
while ! nc -z $DATABASE_HOST 5432
do
  sleep 1
done

sleep 3

DATABASE_HOST=$DATABASE_HOST DATABASE_USER=$DATABASE_USER DATABASE_PASSWORD=$DATABASE_PASSWORD pytest
x=$?

docker kill $CONTAINER
docker rm $CONTAINER

exit $x