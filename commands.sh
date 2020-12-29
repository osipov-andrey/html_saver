docker run -it \
  -v html_files::/app/spider/db/files_storage/html_files \
  --network=host \
  --env-file=.env \
  spider \
  load https://yandex.ru --depth 1

docker run -it \
  -e POSTGRES_DB=mydb \
  -e POSTGRES_USER=andrew \
  -e POSTGRES_PASSWORD=andrew \
  -v html_db_dump:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:12
