from flask import current_app, g
import psycopg2
import os
import uuid
from local_authority_api.exceptions import ApplicationError
from local_authority_api.extensions import db


def update_boundaries_data():
    cwd = os.getcwd()
    connection = db.engine.raw_connection()
    with connection.cursor() as cur:
        try:
            try:
                # Read in the boundaries sql update file
                source_dir = os.path.join(cwd, 'local_authority_api/static')
                g.trace_id = uuid.uuid4().hex
                with open(os.path.join(source_dir, 'boundary_update.sql'), 'r', encoding='utf8') as f:
                    sql_file = f.read()
            except (IOError, OSError) as e:
                g.trace_id = uuid.uuid4().hex
                current_app.logger.exception(str(e))
                return "Error opening " + source_dir

            # split all of the SQL commands and execute them
            sql_commands = sql_file.split(';')
            for command in sql_commands[:-1]:
                cur.execute(command)
            connection.commit()

            current_app.logger.info('Boundaries update completed')

        except psycopg2.Error as e:
            current_app.logger.exception('Application Error: %s', repr(e))
            connection.rollback()
            raise ApplicationError("Boundary update Error", "E999")
        finally:
            connection.close()
