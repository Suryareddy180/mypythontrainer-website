import os
import mysql.connector
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
import shutil

class Command(BaseCommand):
    help = 'Drop all tables from the database and optionally remove migration folders'

    def handle(self, *args, **kwargs):
        # if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        #     self.drop_sqlite_tables()
        # elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        #     self.drop_mysql_tables()
        # else:
        #     self.stdout.write("Unsupported database backend. Only SQLite and MySQL are supported.")

        # Optionally remove migration folders (you can comment this out if not needed)
        for root, dirs, files in os.walk(settings.BASE_DIR):
            if 'migrations' in dirs:
                migration_dir = os.path.join(root, 'migrations')
                self.stdout.write(f"Found migrations directory: {migration_dir}")
                shutil.rmtree(migration_dir)
                self.stdout.write(f"Deleted migrations directory: {migration_dir}")

        self.stdout.write(self.style.SUCCESS("All tables dropped from the database."))

    def drop_sqlite_tables(self):
        """Drop all tables from SQLite database"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("PRAGMA foreign_keys=OFF;")  # Disable foreign key constraints
                tables = connection.introspection.table_names()
                for table in tables:
                    self.stdout.write(f"Dropping table: {table}")
                    cursor.execute(f"DROP TABLE IF EXISTS {table};")
                cursor.execute("PRAGMA foreign_keys=ON;")  # Re-enable foreign key constraints
                self.stdout.write("All tables dropped from SQLite database.")
            except OperationalError as e:
                self.stdout.write(f"Error dropping tables: {e}")

    def drop_mysql_tables(self):
        """Drop all tables from MySQL database"""
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST'] or 'localhost'
        db_port = settings.DATABASES['default']['PORT'] or '3306'

        try:
            connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                port=db_port,
                database=db_name
            )
            cursor = connection.cursor()

            cursor.execute("SET foreign_key_checks = 0;")  # Disable foreign key checks
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            for (table_name,) in tables:
                self.stdout.write(f"Dropping table: {table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            cursor.execute("SET foreign_key_checks = 1;")  # Re-enable foreign key checks

            connection.commit()
            self.stdout.write("All tables dropped from MySQL database.")

        except mysql.connector.Error as err:
            self.stdout.write(f"Error: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                self.stdout.write("MySQL connection closed.")
