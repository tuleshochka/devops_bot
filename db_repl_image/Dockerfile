FROM postgres:latest

RUN mkdir -p /etc/postgresql/ 
RUN chmod 750 /var/lib/postgresql/data

ENTRYPOINT [ "bash", "-c", "\
set -e\n\
cat <<EOF > /etc/postgresql/postgresql.conf \n\
listen_addresses = '*' \n\
port = ${DB_REPL_PORT} \n\
EOF\n\
rm -rf /var/lib/postgresql/data/* \n\
echo ${DB_REPL_PASSWORD} | until pg_basebackup -v -R \\\n\
   -h ${DB_HOST} -p ${DB_PORT} -U ${DB_REPL_USER} -P \\\n\
   -D /var/lib/postgresql/data; do echo \"Waiting for master to connect...\" && sleep 1s; done\n\
docker-entrypoint.sh $@"]

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
