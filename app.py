from flask import Flask, request, session, redirect
from flask import render_template, copy_current_request_context
from flask_socketio import SocketIO, send, emit
import json
import game
from flask_simplelogin import SimpleLogin, login_required
import threading


app = Flask(__name__)
SimpleLogin(app)
app.config['SECRET_KEY'] = '5dsf56f4a6g3sa9§"0ff2'
socketio = SocketIO(app, async_mode="eventlet", async_handlers=True)
ga = game.Game()

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def send_prompt_to_user(data):
    emit("update_current_prompt", json.dumps(data), room=data["recipient"])
    # socketio.sleep(0)


def thread_handling():
    while False:
        socketio.sleep(0)
        socketio.emit("server_display_debug_msg", "ping pong", broadcast=True)
        socketio.sleep(0)
        #print("calling")
    
    


def send_prompt_with_vote_options(data):

    print(ga.main_screen_sid, "send_prompt_with_vote_options", json.dumps(data))

    # eventlet.sleep(0)
    
    emit("server_display_debug_msg", "Ich bin eine Nachricht", room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)

    emit("server_update_prompt_with_vote_options", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)

    recipients = data["recipients"]

    for sid in recipients:
        # eventlet.sleep(0)
        emit("update_current_prompt_with_vote_options",
             json.dumps(data), room=sid)
        socketio.sleep(0)
        # eventlet.sleep(0)
        emit("change_player_view", "player_vote_prompt", room=sid)
        socketio.sleep(0)
        #ventlet.sleep(0)


def overwrite_player_name(data):
    print(data)
    sid = data["sid"]
    # eventlet.sleep(0)
    emit("overwrite_player_name", data["new_player_name"], room=sid)
    # socketio.sleep(0)


def server_add_player(name):
    print(name, ga.main_screen_sid, "WHAAAAAAAAAAAAAAAAAAAH")
    # eventlet.sleep(0)
    emit("server_add_player", name, room=ga.main_screen_sid)
    # socketio.sleep(0)


def server_player_has_submitted_answer(name):
    # eventlet.sleep(0)
    
    emit("server_player_has_submitted_answer", name, room=ga.main_screen_sid)
    # socketio.sleep(0)


def server_everybody_has_given_answer(msg):
    # print("EVERYBODDDDYYYY")
    # eventlet.sleep(0)
    
    emit("server_everybody_has_given_answer",
         "nothing", room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_update_results(data):
    # eventlet.sleep(0)
    emit("server_update_results", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_show_scoreboard(data):
    print(data)
    print(json.dumps(data))
    # eventlet.sleep(0)
    emit("server_show_scoreboard", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


game.em.on("prompt_to_user", send_prompt_to_user)
game.em.on("send_prompt_with_vote_option", send_prompt_with_vote_options)
game.em.on("overwrite_player_name", overwrite_player_name)
game.em.on("server_add_player", server_add_player)
game.em.on("server_player_has_submitted_answer",
           server_player_has_submitted_answer)
game.em.on("server_everybody_has_given_answer",
           server_everybody_has_given_answer)
game.em.on("server_update_results", server_update_results)
game.em.on("server_show_scoreboard", server_show_scoreboard)


@socketio.on("player_connect")
def handle_player_connect(json_string):
    # eventlet.sleep(0)
    # print(request.sid)

    data = json.loads(json_string)
    game.em.emit("player_connect", data["player_name"], request.sid)
    # eventlet.sleep(0)


@socketio.on("start_game")
def handle_game_start():
    
    if (len(ga.connected_players) > 0):
        # eventlet.sleep(0)
        emit("server_start_game_succesful", 1, room=ga.main_screen_sid)
        # socketio.sleep(0)
        # eventlet.sleep(0)
        game.em.emit("start_game")
        #emit("everybody", "Nachricht an alle",broadcast=True)
        # eventlet.sleep(0)
        emit("change_player_view", "player_prompt_answer", broadcast=True)
        # socketio.sleep(0)
        # eventlet.sleep(0)
    else:
        # eventlet.sleep(0)
        emit("server_start_game_succesful", 0, room=ga.main_screen_sid)
        # socketio.sleep(0)
        # eventlet.sleep(0)


@socketio.on("start_vote_loop")
def handle_start_of_vote_loop():
    # eventlet.sleep(0)
    game.em.emit("start_prompt_vote_loop")
    # eventlet.sleep(0)


@socketio.on("prompt_answer")
def handle_prompt_answer(data):
    #{'prompt_answer': 'sdfdsfsfd', 'prompt_id': 0, 'player_name': 'b'}
    prompt_data = json.loads(data)
    # eventlet.sleep(0)
    data_for_function = {"player_id": ga.get_player_id_from_name(prompt_data["player_name"]),
                         "prompt_id": prompt_data["prompt_id"],
                         "answer": prompt_data["prompt_answer"]}

    game.em.emit("player_answer", data_for_function)
    # eventlet.sleep(0)


@socketio.on("player_vote")
def handle_player_vote(data):
     # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
    # eventlet.sleep(0)
    vote_data = json.loads(data)

    data_for_function = {"player_id": ga.get_player_id_from_name(vote_data["player_name"]),
                         "prompt_id": vote_data["prompt_id"],
                         "voted_for": vote_data["option_id"]}
    print("player_vote", data_for_function)
    # eventlet.sleep(0)
    game.em.emit("player_vote", data_for_function)
    # eventlet.sleep(0)


@socketio.on("server_connect")
def handle_server_connect():
    # eventlet.sleep(0)
    socketio.start_background_task(target=thread_handling)
    game.em.emit("start_waiting_for_players")

    ga.main_screen_sid = request.sid

    print("Main Screen has connected",
          ga.main_screen_sid, "WHAAAAAAAAAAAAAAAAAAAAAH")
    # eventlet.sleep(0)


@socketio.on("server_restart_game")
def handle_server_game_restart():
    # eventlet.sleep(0)
    print("Restart pressed")
    ga.reset()
    game.em.emit("start_waiting_for_players")
    emit("player_restart", "nothing", broadcast=True)
    # socketio.sleep(0)
    # eventlet.sleep(0)


@app.route("/play/")
def player_view():
    return render_template("player.html")


@app.route("/main_screen")
@login_required(username="admin")
def main_screen_view():
    return render_template("server.html")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=25565)
