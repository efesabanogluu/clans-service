from flask import Flask, request, jsonify, g
import uuid
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import logging
from config import DB_CONFIG

app = Flask(__name__)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('clans_api')

# Connection Pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="clans_pool",
    pool_size=5,
    **DB_CONFIG
)

def get_db():
    if 'db_conn' not in g:
        g.db_conn = connection_pool.get_connection()
    return g.db_conn

@app.teardown_appcontext
def close_db(e):
    db = g.pop('db_conn', None)
    if db is not None:
        db.close()

# Root Endpoint
@app.route('/')
def home():
    return jsonify({
        "service": "Vertigo Games Clan API",
        "version": "1.0.0",
        "endpoints": {
            "create_clan": {
                "method": "POST",
                "path": "/clans",
                "description": "Create a new clan",
                "parameters": {
                    "body": {
                        "name": {"type": "string", "required": True, "example": "Shadow Warriors"},
                        "region": {"type": "string", "required": False, "example": "TR"}
                    }
                }
            },
            "list_clans": {
                "method": "GET",
                "path": "/clans",
                "description": "List all clans with optional filtering and sorting",
                "parameters": {
                    "query": {
                        "region": {"type": "string", "required": False, "description": "Filter by region code", "example": "US"},
                        "sort": {"type": "string", "required": False, "description": "Sort by 'name' or 'created_at'", "example": "name"}
                    }
                }
            },
            "get_clan": {
                "method": "GET",
                "path": "/clans/<uuid:id>",
                "description": "Get clan details by ID",
                "parameters": {
                    "path": {
                        "id": {"type": "UUID", "required": True, "description": "Clan UUID", "example": "8cff89b6-b986-4a01-a9d6-4d66cff39f8f"}
                    }
                }
            },
            "delete_clan": {
                "method": "DELETE",
                "path": "/clans/<uuid:id>",
                "description": "Delete a clan by ID",
                "parameters": {
                    "path": {
                        "id": {"type": "UUID", "required": True, "description": "Clan UUID", "example": "8cff89b6-b986-4a01-a9d6-4d66cff39f8f"}
                    }
                }
            }
        },
    })

# 1. Creates a new clan and returns the UUID.
@app.route('/clans', methods=['POST'])
def create_clan():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Clan name is required"}), 400
    
    # Assign UUID for clan_id.
    clan_id = str(uuid.uuid4())
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            """INSERT INTO clans (id, name, region, created_at) 
            VALUES (%s, %s, %s, UTC_TIMESTAMP())""",
            (clan_id, data['name'], data.get('region')))
            
        db.commit()
        logger.info(f"Clan created: {clan_id}")
        return jsonify({
            "id": clan_id,
            "message": "Clan created successfully"
        }), 201
        
    except mysql.connector.Error as err:
        db.rollback()
        logger.error(f"MySQL error: {err}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

# 2. Lists all clans. Optionally filter by region or sort by created_at.
@app.route('/clans', methods=['GET'])
def get_clans():
    region = request.args.get('region')
    sort = request.args.get('sort', 'created_at')
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        query = "SELECT id, name, region, created_at FROM clans"
        params = []
        
        if region:
            query += " WHERE region = %s"
            params.append(region)
            
        if sort in ['created_at', 'name']:
            query += f" ORDER BY {sort}"
        
        cursor.execute(query, params)
        clans = cursor.fetchall()
        
        # Convert datetime to ISO format
        for clan in clans:
            clan['created_at'] = clan['created_at'].isoformat() + 'Z'
            
        return jsonify(clans), 200
        
    except mysql.connector.Error as err:
        logger.error(f"MySQL error: {err}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

# 3. Return a clan with a specific id
@app.route('/clans/<uuid:id>', methods=['GET'])
def get_clan(id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT id, name, region, created_at FROM clans WHERE id = %s",
            (str(id),)
        )
        
        clan = cursor.fetchone()
        if not clan:
            return jsonify({"error": "Clan not found"}), 404
            
        clan['created_at'] = clan['created_at'].isoformat() + 'Z'
        return jsonify(clan), 200
        
    except mysql.connector.Error as err:
        logger.error(f"MySQL error: {err}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

# 4. Deletes the clan with the given ID.
@app.route('/clans/<uuid:id>', methods=['DELETE'])
def delete_clan(id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "DELETE FROM clans WHERE id = %s",
            (str(id),)
        )
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Clan not found"}), 404
            
        db.commit()
        logger.info(f"Clan deleted: {id}")
        return jsonify({"message": "Clan deleted successfully"}), 200
        
    except mysql.connector.Error as err:
        db.rollback()
        logger.error(f"MySQL error: {err}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

# curl -X POST https://clans-api-901696881514.europe-west1.run.app/clans \
#   -H "Content-Type: application/json" \
#   -d '{"name":"Phoenix","region":"US"}' \
#   --compressed

#curl "https://clans-api-901696881514.europe-west1.run.app/clans?region=TR&sort=name"

#curl https://clans-api-901696881514.europe-west1.run.app/clans/8cff89b6-b986-4a01-a9d6-4d66cff39f8f

#curl -X DELETE https://clans-api-901696881514.europe-west1.run.app/clans/8cff89b6-b986-4a01-a9d6-4d66cff39f8f
