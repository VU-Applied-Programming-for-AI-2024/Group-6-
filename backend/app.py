from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import requests
import logging
import os
from dotenv import load_dotenv

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)
CORS(app)

load_dotenv()

@app.route('/')
def hello_world():
    """
    Default route to check if the server is running.
    Returns a simple "Hello, World!" message.
    """
    return 'Hello, World!'


def get_db_connection():
    """
    Establish a connection to the SQLite database.
    Set the row factory to sqlite3.Row to access columns by name.
    Returns:
        sqlite3.Connection: A connection object to interact with the database.
    """
    conn = sqlite3.connect('database.db', timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database by creating necessary tables if they do not exist.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        ''')

            # Create Players table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Players (
            
            
    
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    name VARCHAR(255) NOT NULL,               
    position VARCHAR(100),                    
    team VARCHAR(255),                        
    market_value VARCHAR(50),                 
    nationality VARCHAR(100),                 
    height VARCHAR(50),                       
    img TEXT,                             
    birthDate TEXT,                          
    wage VARCHAR(100),                        
    potential VARCHAR(50),                    
    rating VARCHAR(50),                       
    description TEXT,                         
    foot VARCHAR(20)                          



        );
        ''')

        # Create UserPlayers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserPlayers (
            user_id INTEGER,
            player_id INTEGER,  -- Reference to the player ID
            PRIMARY KEY (user_id, player_id),
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE
        );
        ''')


        # Create StartingEleven table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS StartingEleven (
            user_id INTEGER,
            position TEXT,
            player_id INTEGER,
            PRIMARY KEY (user_id, position),
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE
        );
        ''')

# Initialize the database
init_db()

def get_user_id(username):
    """
    Retrieve the user ID based on the username.
    
    Args:
        username (str): The username of the user.
    
    Returns:
        int or None: The user ID if found, None otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM Users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user['user_id']
    return None

@app.route('/search', methods=['GET'])
def search_players():
    """
    Search for players using a SPARQL query and return the results.
    
    Returns:
        JSON: A list of players matching the search query or an error message.
    """
    query = request.args.get('q')
    sparql_endpoint = "http://127.0.0.1:7200/repositories/kd_repo_project"

    sparql_query = f"""
    PREFIX fot: <http://www.example.org/group-27/football-ontology/>
    SELECT ?player ?name ?team ?position ?height ?marketValue ?img ?birth_date ?wage ?potential ?rating ?description ?foot ?nationality
    WHERE {{
        ?player fot:name ?name .
        ?player fot:hasTeam ?team .
        ?player fot:hasPosition ?position .
        ?player fot:height ?height .
        ?player fot:marketValue ?marketValue .
        ?player fot:img ?img .
        ?player fot:birthDate ?birth_date .
        ?player fot:hasWage ?wage .
        ?player fot:hasPotential ?potential .
        ?player fot:hasRating ?rating .
        ?player fot:description ?description .
        ?player fot:foot ?foot .
        OPTIONAL {{?player fot:bornInCountry ?nationality . }}
        FILTER (CONTAINS(LCASE(?name), LCASE("{query}")))  # Case insensitive search
    }}
    LIMIT 10
    """

    try:
        headers = {'Accept': 'application/json'}
        response = requests.post(sparql_endpoint, data={'query': sparql_query}, headers=headers)
        data = response.json()

        if 'results' in data and 'bindings' in data['results']:
            players = [
                {
                    'player': player['player']['value'],
                    'name': player['name']['value'],
                    'team': player['team']['value'],
                    'position': player['position']['value'],
                    'height': player['height']['value'],
                    'marketValue': player['marketValue']['value'],
                    'img': player['img']['value'],
                    'birth_date': player['birth_date']['value'],
                    'wage': player['wage']['value'],
                    'potential': player['potential']['value'],
                    'rating': player['rating']['value'],
                    'description': player['description']['value'],
                    'foot': player['foot']['value'],
                    'nationality': player['nationality']['value'] if 'nationality' in player else 'Unknown to FIFA database.'


                   
                }
                for player in data['results']['bindings']
            ]
            return jsonify(players), 200

        return jsonify({'message': 'No players found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players', methods=['GET'])
def get_players():
    """
    Retrieve all players from the Players table.
    
    Returns:
        JSON: A list of players.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Players')
    players = cursor.fetchall()
    conn.close()

    return jsonify([dict(player) for player in players]), 200


@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user and store their information in the database.
    
    Request Body:
        username (str): The username of the new user.
        password (str): The password of the new user.
    
    Returns:
        JSON: A success message with user ID or an error message.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"message": "Error registering user", "error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """
    Log in a user by checking their username and password against the database.
    
    Request Body:
        username (str): The username of the user.
        password (str): The password of the user.
    
    Returns:
        JSON: A success message with user ID or an error message.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({"message": "Login successful", "user_id": user['user_id']}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 400
    except Exception as e:
        return jsonify({"message": "Error logging in", "error": str(e)}), 500

@app.route('/api/users/<username>/players', methods=['GET'])
def get_user_players(username):
    """
    Retrieve the favorite players of a user based on their username.
    
    Args:
        username (str): The username of the user.
    
    Returns:
        JSON: A list of favorite players or an error message.
    """
    user_id = get_user_id(username)
    if user_id is None:
        return jsonify({"message": "User not found"}), 404
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Players.* 
        FROM Players 
        JOIN UserPlayers ON Players.player_id = UserPlayers.player_id 
        WHERE UserPlayers.user_id = ?
    ''', (user_id,))
    players = cursor.fetchall()
    conn.close()

    return jsonify([dict(player) for player in players]), 200

@app.route('/api/users/<username>/favorite_players', methods=['POST'])
def add_favorite_player(username):
    """
    Add a player to the user's list of favorite players.
    
    Args:
        username (str): The username of the user.
    
    Request Body:
        name (str): The name of the player.
        team (str): The team of the player.
        position (str): The position of the player.
        picture (str, optional): The picture URL of the player.
        nationality (str, optional): The nationality of the player.
        birth_date (str, optional): The birth date of the player.
        height (str, optional): The height of the player.
        weight (str, optional): The weight of the player.
        description (str, optional): The description of the player.
    
    Returns:
        JSON: A success message or an error message.
    """
    logging.debug(f"Adding favorite player for username: {username}")
    user_id = get_user_id(username)
    if user_id is None:
        logging.debug(f"User not found for username: {username}")
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    logging.debug(f"Received data: {data}")
    print(data)
    name = data.get('name')
    team = data.get('team', '').split('/').pop().replace('_', ' ') or 'Unknown Team'
    position = data.get('position', '').split('/').pop() or 'Unknown Position'
    img = data.get('img', None)
    nationality = data.get('nationality', 'Not Available')
    birthDate = data.get('birthDate', 'Unknown Date')
    height = data.get('height', 'Not Available')
    description = data.get('description', 'No Description')
    


    if not name:
        return jsonify({"message": "Player name is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("DATA", data)
        # Insert player and get the player_id of the new entry
        # Insert player and get the player_id of the new entry
        cursor.execute('''
    INSERT INTO Players 
    (name, team, position, img, nationality, birthDate, height, description, market_value, potential, rating, foot, wage)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (name, team, position, img, nationality, birthDate, height, description, 
      data.get('market_value', 'Not Available'),
      data.get('potential', 'Not Available'), 
      data.get('rating', 'Not Available'), 
      data.get('foot', 'Not Specified'),
      data.get('wage', 'Not Available')))


        
        # Get the last inserted player_id
        player_id = cursor.lastrowid
        
        # Now insert into UserPlayers with user_id and player_id
        cursor.execute('INSERT INTO UserPlayers (user_id, player_id) VALUES (?, ?)', (user_id, player_id))
        
        conn.commit()
        conn.close()
        logging.debug(f"Player {name} added to favorites for username: {username}")
        return jsonify({"message": "Player added to favorites"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": "Player already in favorites"}), 400
    except Exception as e:
        logging.error(f"Error adding player to favorites: {e}")
        return jsonify({"message": "Error adding player to favorites", "error": str(e)}), 500

@app.route('/api/news')
def get_latest_news():
    """
    Fetch and return the latest football news from an external API.
    
    Returns:
        JSON: A list of news articles or an error message.
    """
    try:
        response = requests.get('https://footballnewsapi.netlify.app/.netlify/functions/api/news/espn')
        if not response.ok:
            raise Exception('Failed to fetch news')
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<username>/favorite_players', methods=['DELETE'])
def remove_favorite_player(username):
    """
    Remove a player from the user's list of favorite players.
    
    Args:
        username (str): The username of the user.
    
    Request Body:
        name (str): The name of the player to be removed.
    
    Returns:
        JSON: A success message or an error message.
    """
    user_id = get_user_id(username)
    if user_id is None:
        logging.debug(f"User not found for username: {username}")
        return jsonify({"message": "User not found"}), 404

    # Ensure the request content type is application/json
    if not request.is_json:
        return jsonify({"message": "Invalid request format, JSON required"}), 400

    data = request.get_json()
    logging.debug(f"Received data for removal: {data}")
    name = data.get('name')  # Extract player's name from JSON body
    
    if not name:
        logging.debug("Player name is required but not provided")
        return jsonify({"message": "Player name is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the player_id from the Players table based on the name
        cursor.execute('SELECT player_id FROM Players WHERE name = ?', (name,))
        player = cursor.fetchone()

        if player is None:
            logging.debug(f"No player found with name: {name}")
            return jsonify({"message": "Player not found"}), 404

        player_id = player[0]

        # Remove the player from UserPlayers table
        cursor.execute('DELETE FROM UserPlayers WHERE user_id = ? AND player_id = ?', (user_id, player_id))
        rows_affected = cursor.rowcount
        
        if rows_affected == 0:
            conn.close()
            logging.debug(f"No player found with player_id: {player_id} for user_id: {user_id}")
            return jsonify({"message": "Player not found in favorites"}), 404
        
        # Check if the player is still favorited by any other user
        cursor.execute('SELECT COUNT(*) FROM UserPlayers WHERE player_id = ?', (player_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Remove the player from Players table if no other user has favorited this player
            cursor.execute('DELETE FROM Players WHERE player_id = ?', (player_id,))
            logging.debug(f"Player {player_id} removed from Players table")
        
        conn.commit()
        conn.close()

        logging.debug(f"Player {name} removed from favorites for user {user_id}")
        return jsonify({"message": "Player removed from favorites"}), 200
    except Exception as e:
        logging.error(f"Error removing player from favorites: {e}")
        return jsonify({"message": "Error removing player from favorites", "error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Retrieve all users from the Users table.
    
    Returns:
        JSON: A list of users.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    conn.close()

    return jsonify([dict(user) for user in users]), 200

@app.route('/api/startingeleven/<username>', methods=['GET'])
def get_starting_eleven(username):
    """
    Retrieve the starting eleven players for a user based on their username.
    
    Args:
        username (str): The username of the user.
    
    Returns:
        JSON: A list of starting eleven players or an error message.
    """
    user_id = get_user_id(username)
    if user_id is None:
        return jsonify({"message": "User not found"}), 404
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT StartingEleven.position, Players.player_id, Players.name, Players.img
        FROM StartingEleven
        JOIN Players ON StartingEleven.player_id = Players.player_id
        WHERE StartingEleven.user_id = ?
    ''', (user_id,))
    starting_eleven = cursor.fetchall()
    conn.close()

    result = [{"position": row["position"], "player_id": row["player_id"], "name": row["name"], "picture": row["img"]} for row in starting_eleven]
    return jsonify(result), 200

@app.route('/api/startingeleven/<username>', methods=['POST'])
def add_to_starting_eleven(username):
    """
    Add a player to the user's starting eleven.
    
    Args:
        username (str): The username of the user.
    
    Request Body:
        position (str): The position in the starting eleven.
        player_id (int): The ID of the player to be added.
    
    Returns:
        JSON: A success message or an error message.
    """
    user_id = get_user_id(username)
    if user_id is None:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    position = data.get('position')
    player_id = data.get('player_id')

    if not position or not player_id:
        return jsonify({"message": "Position and player ID are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO StartingEleven (user_id, position, player_id)
            VALUES (?, ?, ?)
        ''', (user_id, position, player_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Player added to starting eleven", "player_id": player_id, "position": position}), 200
    except Exception as e:
        return jsonify({"message": "Error adding player to starting eleven", "error": str(e)}), 500

@app.route('/api/startingeleven/<username>/<position>', methods=['DELETE'])
def remove_from_starting_eleven(username, position):
    """
    Remove a player from the user's starting eleven.
    
    Args:
        username (str): The username of the user.
        position (str): The position to be cleared in the starting eleven.
    
    Returns:
        JSON: A success message or an error message.
    """
    user_id = get_user_id(username)
    if user_id is None:
        return jsonify({"message": "User not found"}), 404

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM StartingEleven 
            WHERE user_id = ? AND position = ?
        ''', (user_id, position))
        conn.commit()
        conn.close()
        return jsonify({"message": "Player removed from starting eleven"}), 200
    except Exception as e:
        return jsonify({"message": "Error removing player from starting eleven", "error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
