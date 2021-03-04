#!/bin/sh

# git checkout dev

staging_db_user=$STAGING_DB_USER
staging_db_pwd=$STAGING_DB_PASSWORD
staging_db_db=$STAGING_DB_DATABASE
staging_db_host=$STAGING_DB_PUBLIC_HOST

db_user=$PROD_DB_USER
db_pwd=$PROD_DB_PASSWORD
db_db=$PROD_DB_DATABASE
db_host=$PROD_DB_PUBLIC_HOST
now=$(date +%s)

# Get current alembic version for staging db
alembic_staging_current=$(mysql -u ${staging_db_user} -p${staging_db_pwd} -h ${staging_db_host} -D ${staging_db_db} -e "Select version_num from alembic_version;" -s -N)
alembic_staging_current=${alembic_staging_current:0:12}

# Show tables
# check_alembic=$(mysql --login-path=prod -D ${db_db} -e "Select TABLE_NAME from information_schema.tables where TABLE_NAME ='alembic_version';" -s -N)
check_alembic=$(mysql -u ${db_user} -p${db_pwd} -h ${db_host} -D ${db_db} -e "Select TABLE_NAME from information_schema.tables where TABLE_NAME ='alembic_version';" -s -N)

if [ "alembic_version" == "$check_alembic" ]; then
    echo "Alembic Version table exists in prod db!"

    # Get current alembic version for prod db
    alembic_prod_version=$(mysql -u ${db_user} -p${db_pwd} -h ${db_host} -D ${db_db} -e "Select version_num from alembic_version;" -s -N)

    if [ "$alembic_prod_version" == "$alembic_staging_current" ]; then
        echo "Prod DB is already up to date!"
    else
        echo "Updating Prod DB to $alembic_staging_current revision"

        # Generate sql migration script
        sql_migration_script=$(alembic upgrade $alembic_prod_version:$alembic_staging_current --sql)

        # Execute SQL migration script
        mysql -u ${db_user} -p${db_pwd} -h ${db_host} -D ${db_db} -e "$sql_migration_script"
    fi
else
    echo "Alembic Version table does not exist"

    # Generate sql migration script
    sql_migration_script=$(alembic upgrade $alembic_staging_current --sql)

    # Execute SQL migration script
    mysql -u ${db_user} -p${db_pwd} -h ${db_host} -D ${db_db} -e "$sql_migration_script"
fi

git checkout main && git merge staging && git checkout dev

# venv/bin/python3 deploy/prod/staging_db_setup.py