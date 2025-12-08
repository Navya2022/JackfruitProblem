import firebase_admin
from firebase_admin import credentials ,db
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL":"https://jackfruit-443a7-default-rtdb.asia-southeast1.firebasedatabase.app/"})

def checkUser(username, password):
    status = "Failed"
    player_ref = db.reference('/')
    all_players = player_ref.get()

    if not all_players:
        return None

    for player_id, player_data in all_players.items():
        if (player_data.get("username") == username and
                player_data.get("password") == password):
            status = "Success"
    return status

def addUser(username,password,avatarid):
    player_ref = db.reference('/')
    user = {
    "username": username,
    "password": password,
    "avatarId": avatarid,
    "level": 0 }
    new_user = player_ref.push(user)
    return new_user.key

def updateMarks(username,level):
    player_ref = db.reference('/')
    all_players = player_ref.get()

    if not all_players:
        return None

    for player_id, player_data in all_players.items():
        if (player_data.get("username") == username):
            player_ref.child(player_id).update({"level": player_data.get("level")+level})
            return "Success"
    return "Failed"

def getLevel(username):
    player_ref = db.reference('/')
    all_players = player_ref.get()

    if not all_players:
        return None

    for player_id, player_data in all_players.items():
        if (player_data.get("username") == username):
            return player_data.get("level")
    return None
