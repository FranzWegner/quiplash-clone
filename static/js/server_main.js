let all_divs = []
let connected_players = []

let prompt_answer_countdown = 90
let all_answers_given = false

let vote_countdown = 0
let current_prompt = "The worst thing a plastic surgeon could say after he botched your surgery: \u201cI\u2019m sorry, I accidentally <BLANK>"
let current_options = ["Hallo", "Zwei Worte", "Drei Worte hier"]

let current_options_authors = []
let current_options_voters = []
let current_options_points = []

let current_scores = {}


let voting_period_ended = false


function clear_all_values() {
    connected_players = []

    all_answers_given = false

    current_prompt = ""
    current_options = []

    current_options_authors = []
    current_options_voters = []
    current_options_points = []

    current_scores = {}
}

function start_new_game() {
    start_prompt_answer_countdown(prompt_answer_countdown)

    set_active_screen('server_waiting_for_player_input')
}

function update_scoreboard() {
    let scores_list = document.querySelector("#server_scoreboard")
    scores_list.innerText = ""

    // sort by scores https: //stackoverflow.com/questions/1069666/sorting-javascript-object-by-property-value
    let sortable = [];
    for (let player in current_scores) {
        sortable.push([player, current_scores[player]]);
    }

    sortable.sort(function(a, b) {
        return b[1] - a[1];
    });

    for (let i = 0; i < sortable.length; i++) {
        let node = document.createElement("LI")
        let score_node = document.createTextNode("" + sortable[i][0] + " | " + sortable[i][1])
        node.appendChild(score_node)

        scores_list.appendChild(node)
    }


}

function update_results(data) {

    current_options_authors = []
    current_options_voters = []
    current_options_points = []

    for (let i = 0; i < Object.keys(data).length; i++) {

        current_options_authors.push(data[i]["author"])
        current_options_voters.push(data[i]["voters"])
        current_options_points.push(data[i]["points"])

    }

    console.log(current_options_authors, current_options_voters, current_options_points)
    show_updated_results()

}

function show_updated_results() {

    // TO DO CLEAN THE FUCK UP

    let author_list = document.querySelector("#server_options_authors")
    author_list.innerText = ""

    for (author of current_options_authors) {

        let node = document.createElement("LI")
        let author_node = document.createTextNode(author)
        node.appendChild(author_node)

        node.id = "author_" + player



        author_list.appendChild(node)

    }

    let voters_list = document.querySelector("#server_options_voters")
    voters_list.innerText = ""

    for (voters of current_options_voters) {

        let node = document.createElement("LI")
        let voters_node = document.createTextNode(voters)
        node.appendChild(voters_node)
        voters_list.appendChild(node)

    }

    let points_list = document.querySelector("#server_options_points")
    points_list.innerText = ""

    for (points of current_options_points) {

        let node = document.createElement("LI")
        let points_node = document.createTextNode(points)
        node.appendChild(points_node)
        points_list.appendChild(node)

    }

}

async function start_vote_countdown(seconds) {
    while (seconds > 0) {


        if (voting_period_ended == true) {
            console.log("votes givennnn")
            break
        }

        await Sleep(1000)
        seconds--
        document.querySelector("#server_countdown_prompt").innerText = seconds





    }
    console.log("Waiting for results event")
    voting_period_ended = false
    vote_countdown = 15
    document.querySelector("#server_countdown_prompt").innerText = 15
}

async function start_prompt_answer_countdown(seconds) {


    while (seconds > 0) {

        // is true, when socket get the event from server
        if (all_answers_given == true) {
            console.log("answers givennnn")
            break
        }

        await Sleep(1000)
        seconds--
        document.querySelector("#server_countdown_player_input").innerText = seconds




    }
    all_answers_given = false
    console.log("Start Vote Loop")
    start_vote_loop()

}

function Sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function make_player_appear_bold(player_name) {
    document.getElementById("player_" + player_name).style.fontWeight = "bold"
}

function make_player_appear_with_background_color(player_name) {
    document.getElementById("player_" + player_name).style.backgroundColor = "#b0bbe8"
}

function generate_player_list_waiting_for_player_input() {


    let players_list = document.querySelector("#server_waiting_for_player_input_list")
    players_list.innerText = ""

    for (player of connected_players) {

        let node = document.createElement("LI")
        let player_node = document.createTextNode(player)
        node.appendChild(player_node)

        node.id = "player_" + player



        players_list.appendChild(node)

    }

}

function add_player_to_display(name) {
    let players_list = document.querySelector("#server_waiting_for_players_list")

    let node = document.createElement("LI")
    let player_node = document.createTextNode(name)
    node.appendChild(player_node)
    players_list.appendChild(node)

}


function add_player(name) {

    connected_players.push(name)
    add_player_to_display(name)

}

function set_all_divs() {


    all_divs = document.getElementsByTagName("div");


}

function set_active_screen(div_id) {

    console.log("Changing screen to ", div_id)

    display_prompt(current_prompt)
    display_options(current_options)

    for (div of all_divs) {

        if (div.id == div_id) {

            div.style.display = "block"

        } else {
            div.style.display = "none"
        }

    }

}

function display_options(options) {

    let list = document.getElementsByClassName("server_current_options")

    for (let j = 0; j < list.length; j++) {

        let new_list_of_options = ""

        for (let i = 0; i < current_options.length; i++) {
            let line_to_attach = "<li id='vote_option_" + (i + 1) + "'>" + current_options[i] + "</li>"

            //<li id="vote_option_1">Option 1</li>
            new_list_of_options += line_to_attach;

        }
        list[j].innerHTML = new_list_of_options;
    }

}

function display_prompt(prompt) {

    // TO DO clean it up
    document.getElementsByClassName("server_current_prompt")[0].innerText = current_prompt
    document.getElementsByClassName("server_current_prompt")[1].innerText = current_prompt

}

window.onload = () => {

    console.log("JS start now")

    set_all_divs()
    set_active_screen('server_start')

    document.querySelector("#server_start").onclick = () => {

        console.log("New Game Button pressed")
        set_active_screen('server_waiting_for_players')

        //connect_to_socket('http://192.168.0.119:25565')
        connect_to_socket('http://91.64.111.47:25565')



    }

    document.querySelector("#server_start_game").onclick = () => {

        console.log("Start Game Button pressed")

        generate_player_list_waiting_for_player_input()

        start_game()



    }

    document.querySelector("#server_restart").onclick = () => {

        console.log("Restart Game Button pressed")

        // clear everything
        clear_all_values()
        document.querySelector("#server_waiting_for_players_list").innerText = ""

        restart_game()

        set_active_screen('server_waiting_for_players')





    }


}