class Player: 
    player_name = ""
    player_score = 0
    ip_adress = ""
    player_id = -1
    prompt_answers = {}
    player_sid = None

    def __init__(self,name,sid):
        self.player_name = name
        self.player_sid = sid
    
    def add_points(self,amount):
        self.player_score += amount     