# Local Authority API

### Common dev env
This application is built to run on our common development environment (common dev-env), which you can read more about here: https://github.com/LandRegistry/common-dev-env

### Alembic

To create a new alembic revision to the database from console in _dev-env_:
```bash
manage local-authority-api db revision
```

### Upgrading / Downgrading

To upgrade the database from console in _dev-env_:
```bash
docker-compose exec -T local-authority-api /bin/bash -c "PGUSER=root PGPASSWORD=superroot SQL_USE_ALEMBIC_USER=yes SQL_PASSWORD=superroot python3 manage.py db upgrade"
```

To downgrade the database (one revision at a time) from console in _dev-env_:
```bash
docker-compose exec -T local-authority-api /bin/bash -c "PGUSER=root PGPASSWORD=superroot SQL_USE_ALEMBIC_USER=yes SQL_PASSWORD=superroot python3 manage.py db downgrade"
```

### Revision Creation Consistency Notes
1. Keep table names singular noun
2. Primary Keys are indexed automatically
3. Create foreign keys using sa.ForeignKey() notation for automatic naming

### Documentation

The API has been documented using swagger YAML files. The swagger files can be found under the [documentation](local_authority_api/documentation) directory. To edit or view the documentation open the YAML file in swagger.io <http://editor.swagger.io>

## Linting

Linting is performed with [Flake8](http://flake8.pycqa.org/en/latest/). To run linting:
```
docker-compose exec local-authority-api make lint
```


## Data Loading
Data can be loaded into the database using alembic migration files, instead of the previously used `setup_db.sh` script. However, see Boundary updates section for updates that need to take place after migrations.

The current approach for this is to create a list or dictionary at the top of the migration file containing the data to be added which can be used in both the upgrade and downgrade methods.

One issue that arises when doing this is that escape characters are different in python and SQL which needs to be accounted for when deleting rows using the same list that they were added with. For example, to escape an apostrophe for SQL in a string that contains the python version, the following can be used:

```python
string.replace("\'", "\'\'")
```

There are a number of shapefiles external to the migration scripts used for loading boundary data. The naming convention for such files is:

`<migration-revision-id>_<name>.<extension>`

## Boundary updates
Boundary updates should run on starting up your development environment, but to manually run them use:
```docker exec -i local-authority-api python3 manage.py update_boundaries```
