import player
import random
import event_emitter as events
import time
import sched
import threading
from random_word import RandomWords
import db
from flask import copy_current_request_context
import eventlet

r = RandomWords()
s = sched.scheduler(time.time, time.sleep)
em = events.EventEmitter()

testMode = False


class Game:
    max_players = 8
    prompts_to_play = 0
    main_screen_sid = None
    # player_id start with 1
    connected_players = []
    # prompts start with 0
    prompts = []
    prompt_assignments = []

    answer_counter = 0

    prompt_answers = {}

    events_thread = None
    prompt_vote_loop_thread = None
    i_am_listening = False
    waiting_for_user_input = False

    # -1 unstarted, 0 = wait for more player, 1 = wait for player input, 2 = showing prompt, 3 = showing prompt + voting result
    game_state = -1

    def __init__(self):
        self.events_thread = threading.Thread(None, self.events_handler)
        self.events_thread.start()

    def reset(self):
        self.max_players = 8
        self.prompts_to_play = 0

        self.connected_players = []

        self.prompts = []
        self.prompt_assignments = []

        self.answer_counter = 0

        self.prompt_answers = {}

    def start_event_listener(self):
        print("Now listening for internal events")

    def countdown_function(self, seconds):
        countdown = seconds

        while countdown > 0:
            time.sleep(1)
            countdown -= 1
            print(countdown)
        em.emit("start_prompt_vote_loop", "dummy_message")

    def events_handler(self):
        self.i_am_listening = True
        # events

        em.on("player_connect", self.add_connected_player)
        em.on("start_game", self.start_game)
        em.on("debug_msg", self.print_debug)
        em.on("player_answer", self.add_player_answer)
        em.on("player_vote", self.add_player_vote)
        em.on("change_game_state", self.set_game_state)
        em.on("start_waiting_for_players", self.start_waiting_for_players)
        em.on("start_prompt_vote_loop", self.start_prompt_vote_loop)

        while True:
            if self.waiting_for_user_input == True:
                pass
                # print("i am waiting for user input")

    def start_prompt_vote_loop_thread(self):
        self.prompt_vote_loop_thread = threading.Thread(
            None, self.start_prompt_vote_loop)
        self.prompt_vote_loop_thread.start()

    def get_player_id_from_name(self, name):
        for player in self.connected_players:
            if player.player_name == name:
                return player.player_id

    def send_prompts_to_players(self):
        for index, player_id_list in enumerate(self.prompt_assignments):
            prompt_to_send = self.prompts[index]
            for player in player_id_list:
                sid = self.connected_players[player-1].player_sid
                em.emit("prompt_to_user", {
                        "prompt_text": prompt_to_send, "recipient": sid, "prompt_id": index})

    def calc_points_for_prompt(self, prompt_id):
      #  print(self.prompts[prompt_id])
       # print(self.prompt_answers[prompt_id][0]["voters"])

        overall_voters_amount = 0

        for answer in self.prompt_answers[prompt_id]:
            # print(answer["voters"])
            overall_voters_amount += len(answer["voters"])

            if (overall_voters_amount == 0):
                overall_voters_amount = 1

       # print(overall_voters_amount)

        for answer in self.prompt_answers[prompt_id]:
            author_id = answer["author"]
            amount_of_votes = len(answer["voters"])

            calc_points = round(
                (amount_of_votes / overall_voters_amount) * 100)

            self.connected_players[author_id-1].add_points(calc_points)
            print(
                self.connected_players[author_id-1].player_name, "gets", calc_points, "points.")

        # self.print_connected_player()

    def get_assigned_prompt_id(self, player_id):

        result_prompt_id = None

        for prompt_id, assignments in enumerate(self.prompt_assignments):
            for players in assignments:
                if (players == player_id):
                    result_prompt_id = prompt_id

        return result_prompt_id

    def set_game_state(self, state_id):
        self.game_state = state_id
        print("Game State: ", self.game_state)

        if (self.game_state == 4):
            print("GAME OVER!")
            self.print_connected_player()
            em.emit("change_game_state", -1)

    def all_players_have_given_answer(self):

        if (self.answer_counter == len(self.connected_players)):
            return True
        else:
            return False

    def add_player_answer(self, answer):
        # answer: player_id, prompt_id, submitted_answer
        # EXAMPLE {"player_id": 1, "prompt_id": 1, "answer": "Creative Answer"
        answer_object = {
            "answer": answer["answer"], "author": answer["player_id"], "voters": [], "points": -1}
        self.prompt_answers[answer["prompt_id"]].append(answer_object)

        em.emit("server_player_has_submitted_answer",
                self.connected_players[answer["player_id"]-1].player_name)

        self.answer_counter += 1

        if (self.all_players_have_given_answer()):
            # working
            em.emit("server_everybody_has_given_answer", "nothing")

        print(self.prompt_answers)

    def add_player_vote(self, vote):
       # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
        print("add_player_vote", vote)
        self.prompt_answers[vote["prompt_id"]][vote["voted_for"]]["voters"].append(
            vote["player_id"])

    def print_debug(self):
        print("debug msg")

    def add_connected_player(self, name, sid):
        # TO DO check if SID is already stored
        if (self.game_state == 0 and (len(self.connected_players) <= (self.max_players-1))):

            # check if name is in use, if yes, attach "_"
            for p in self.connected_players:
                if p.player_name == name:
                    name = name + "_"
                    em.emit("overwrite_player_name", {
                            "new_player_name": name, "sid": sid})

            self.connected_players.append(player.Player(name, sid))

            # set player id
            self.connected_players[len(
                self.connected_players)-1].player_id = len(self.connected_players)

            # add to main screen
            em.emit("server_add_player", name)

            print("New Player:", name)
            self.print_connected_player()
        else:
            print("No new players are allowed")
            # TO DO send message to players and reset their view

    def print_connected_player(self):
        for p in self.connected_players:
            print(p.player_id, p.player_name, p.player_score, p.player_sid)

    def assign_players_to_prompts(self):

        p_a = [None] * len(self.prompts)
        player_index = len(self.connected_players)
        i = 0
        while i < len(self.prompts):

            p_list = []

            # clean up
            p_list.append(player_index)
            player_index = player_index - 1
            p_list.append(player_index)
            player_index = player_index - 1

            if player_index == 1:
                p_list.append(player_index)
                player_index = player_index - 1

            p_a[i] = p_list
            i = i + 1

        self.prompt_assignments = p_a

    def calc_prompts_amount(self, player_amount):
        if player_amount % 2 == 1:
            player_amount = player_amount - 1

        return int(player_amount / 2)

    def select_prompts(self):
        allPrompts = db.get_prompts_by_usages(4, True)
        random.shuffle(allPrompts)
        return allPrompts[:self.prompts_to_play]

    def start_waiting_for_players(self):
        # NEW GAME
        em.emit("change_game_state", 0)

        # let the players connect
        if (testMode):
            for n in range(1, random.randint(8, 8)):
                em.emit("player_connect", get_random_name())

        # time.sleep(20)

    def start_countdown(self, seconds):

        countdown_thread = threading.Thread(
            target=self.countdown_function, args=(seconds,))
        countdown_thread.start()

    def start_game(self):
        em.emit("change_game_state", 1)

        self.prompts_to_play = self.calc_prompts_amount(
            len(self.connected_players))
        self.prompts = self.select_prompts()

        # make prompt_answers as big as prompts
        self.prompt_answers = [[]] * len(self.prompts)

        for i in range(0, len(self.prompt_answers)):
            self.prompt_answers[i] = []

        self.assign_players_to_prompts()

        # send prompts to users
        self.send_prompts_to_players()

        # wait for XX seconds

        # simulated player answers

        if (testMode):
            for player in self.connected_players:
                for_which_prompt = self.get_assigned_prompt_id(
                    player.player_id)
                em.emit("player_answer", {
                        "player_id": player.player_id, "prompt_id": for_which_prompt, "answer": r.get_random_word()})

        print(self.prompt_answers)

        # self.start_countdown(15)

        # wait for user input
        # self.start_waiting_for_input(1)

        # simulate user input

        # print("los gehts mit prompts")

    def player_id_to_name(self, player_id):
        return self.connected_players[player_id-1].player_name

    def everybody_voted_for_prompt(self, prompt_id):
        player_amount = len(self.connected_players)
        answers_amount = len(self.prompt_answers[prompt_id])
        votes_amount = 0
        for answer in self.prompt_answers[prompt_id]:
            votes_amount += len(answer["voters"])

        if (votes_amount == (player_amount-answers_amount)):
            return True
        else:
            return False

    def start_prompt_vote_loop(self):
        em.emit("change_game_state", 2)

        for prompt_id, prompt in enumerate(self.prompts):
            print("Prompt:", prompt)

            options_list = []
            options_amount = 0
            for answer in self.prompt_answers[prompt_id]:
                print("Option:", answer["answer"])
                options_amount += 1
                options_list.append(answer["answer"])

            players_who_can_vote = []

            for player in self.connected_players:
                if prompt_id == self.get_assigned_prompt_id(player.player_id):
                    pass
                else:
                    players_who_can_vote.append(player.player_sid)

            time_to_vote = 15

            prompt_with_vote_options = {
                "prompt_text": self.prompts[prompt_id],
                "prompt_id": prompt_id,
                "vote_options": options_list,
                "recipients": players_who_can_vote,
                "time_to_vote": time_to_vote
            }

            # check who can vote for this
            em.emit("send_prompt_with_vote_option", prompt_with_vote_options)

            # user votes

            if (testMode):
                for player in self.connected_players:
                    player_id = player.player_id

                    if (prompt_id == self.get_assigned_prompt_id(player_id)):
                        pass
                    else:
                        i_vote_for = random.randint(0, options_amount-1)-1
                        em.emit("player_vote", {
                                "player_id": player_id, "prompt_id": prompt_id, "voted_for": i_vote_for})

            # time.sleep(time_to_vote+1)

            # check for votes given

            vote_countdown = time_to_vote

            while (vote_countdown > 0):
                print(vote_countdown)

                if(self.everybody_voted_for_prompt(prompt_id)):
                    break

                eventlet.sleep(1)
                vote_countdown -= 1

            em.emit("change_game_state", 3)

            self.calc_points_for_prompt(prompt_id)

            print("Prompt:", prompt)

            data_to_display_on_main_screen = {

            }

            data_counter = 0

            for answer in self.prompt_answers[prompt_id]:

                voters_string = ""

                for index, voter_id in enumerate(answer["voters"]):
                    voters_string += self.player_id_to_name(voter_id)
                    if (index+1 == len(answer["voters"])):
                        pass
                    else:
                        voters_string += ", "

                data_to_add = {
                    "answer": answer["answer"],
                    "author": self.player_id_to_name(answer["author"]),
                    "voters": voters_string,
                    # TO DO show added points, not overall
                    "points": self.connected_players[answer["author"]-1].player_score
                }

                data_to_display_on_main_screen[str(data_counter)] = data_to_add
                data_counter += 1

                print("Option:", answer["answer"], "|",
                      "Votes: ", len(answer["voters"]))

            # for display need: author, voters, points
            print(data_to_display_on_main_screen)
            em.emit("server_update_results", data_to_display_on_main_screen)

            # wait 7 seconds, to begin next iteration, to show results on main screen
            eventlet.sleep(7)

            if (prompt_id == len(self.prompts)-1):
                em.emit("change_game_state", 4)
                em.emit("server_show_scoreboard", self.get_scoreboard())
            else:
                em.emit("change_game_state", 2)

    def get_scoreboard(self):
        object_to_build = {}
        for player in self.connected_players:
            object_to_build[player.player_name] = player.player_score

        return object_to_build

    def start_waiting_for_input(self, countdown_time):
        self.waiting_for_user_input = True
        print("cD start")

        # wait xx second
        time.sleep(countdown_time)

        self.waiting_for_user_input = False
        print("cD stop")


sampleNames = ["Jene",
               "Chase",
               "Chester",
               "Linda",
               "Amal",
               "Jaqueline",
               "Adaline",
               "Eldridge",
               "Shirley",
               "Ronni",
               "Brendan",
               "Sheba",
               "Arden",
               "Herbert",
               "Lona",
               "Judson",
               "Brandi",
               "Mee",
               "Francine",
               "Joeann"]


def get_random_name():
    return random.choice(sampleNames)


def read_prompts_into_list(filename):
    lineList = [line.rstrip('\n') for line in open(filename)]
    return lineList
    # for l in lineList:
    # print(l)


#tGame = Game()

""" while tGame.i_am_listening == False:
    print("not ready yet")

# add random test players
for n in range(1, random.randint(9, 9)):
    em.emit("player_connect", get_random_name())

tGame.print_connected_player()

def waiting():
    while True:
     if tGame.waiting_for_user_input:
         print("is true")

fakeThread = threading.Thread(None, waiting) """
# fakeThread.start()

# em.emit("start_waiting_for_players")
#em.emit("player_answer", {"player_id": 1, "prompt_id": 1, "answer": "Creative Answer"})
#em.emit("player_vote", {"player_id": 0, "prompt_id": 1, "voted_for": 0})

# add random answers

""" for player in tGame.connected_players:
    for_which_prompt = tGame.get_assigned_prompt_id(player.player_id)
    em.emit("player_answer", {"player_id": player.player_id, "prompt_id": for_which_prompt, "answer": r.get_random_word()})

# print(r.get_random_word())

#print(tGame.get_assigned_prompt_id(4))

#add random vote

for player in tGame.connected_players:
    id_of_my_prompt = for_which_prompt = tGame.get_assigned_prompt_id(player.player_id)

    for index, prompt in enumerate(tGame.prompt_assignments):
        if (index == id_of_my_prompt):
            pass
        else:
            vote_options = len(tGame.prompt_assignments[index])
            i_vote_for = random.randint(0, vote_options-1)-1
            em.emit("player_vote", {"player_id": player.player_id, "prompt_id": index, "voted_for": i_vote_for})


print (tGame.prompt_answers)

for index, prompt in enumerate(tGame.prompts):
    tGame.calc_points_for_prompt(index)

tGame.print_connected_player() """
