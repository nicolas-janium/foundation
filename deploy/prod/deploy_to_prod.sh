#!/bin/sh

git checkout dev

# Get current alembic version for dev db
alembic_dev_current=`alembic current | tail -n 1`
alembic_dev_current=${alembic_dev_current:0:12}

db_user=$STAGING_DB_USER
db_pwd=$STAGING_DB_PASSWORD
db_db=$STAGING_DB_DATABASE
db_host=$STAGING_DB_PUBLIC_HOST
now=$(date +%s)

# Show tables
check_alembic=$(mysql --login-path=staging -D ${db_db} -e "Select TABLE_NAME from information_schema.tables where TABLE_NAME ='alembic_version';" -s -N)
if [ "alembic_version" == "$check_alembic" ]; then
    echo "Alembic Version table exists"

    # Get current alembic version for staging db
    alembic_staging_version=$(mysql --login-path=staging -D ${db_db} -e "Select version_num from alembic_version;" -s -N)

    if [ "$alembic_staging_version" == "$alembic_dev_current" ]; then
        echo "Staging DB already up to date!"
    else
        echo "Updating Staging DB to $alembic_dev_current revision"

        # Generate sql migration script
        sql_migration_script=$(alembic upgrade $alembic_staging_version:$alembic_dev_current --sql)

        # Execute SQL migration script
        mysql --login-path=staging -D ${db_db} -e "$sql_migration_script"
    fi
else
    echo "Alembic Version table does not exist"

    # Generate sql migration script
    sql_migration_script=$(alembic upgrade $alembic_dev_current --sql)

    # Execute SQL migration script
    mysql --login-path=staging -D ${db_db} -e "$sql_migration_script"
fi

git checkout staging && git merge dev && git checkout dev

venv/bin/python3 deploy/staging/staging_db_setup.py