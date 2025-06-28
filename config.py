import os
# Configs retrieved from environment variables
DB_CONFIG = {
    'unix_socket': os.getenv('DB_SOCKET', '/cloudsql/omega-booster-464215-u4:us-central1:vertigo-master'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'vertigo_db'),
    'autocommit': False,
    'charset': 'utf8mb4'
}