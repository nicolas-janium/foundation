db_user=$DB_USER
db_pwd=$DB_PASSWORD
now=$(date +%s)

# Get current alembic version for staging db
alembic_staging_current=$(mysql -u ${db_user} -p${db_pwd} -h 35.192.0.205 -D staging -e "Select version_num from alembic_version;" -s -N)

# Get current alembic version for dev db
alembic_dev_current=`alembic current | tail -n 1`
alembic_dev_current=${alembic_dev_current:0:12}

# Create migration file
alembic upgrade ${alembic_staging_current}:${alembic_dev_current} --sql >> db_migrations/migration_staging_${now}_${alembic_dev_current}.sql

# Execute the migration file in the staging db
migration_file=`ls -t db_migrations | head -n 1`
migration_file_path="/home/nicolas/projects/janium/main/db_migrations/${migration_file}"
mysql -u ${db_user} -p${db_pwd} -h 35.192.0.205 -D staging < ${migration_file_path}