let current_prompt = "The worst thing a plastic surgeon could say after he botched your surgery: \u201cI\u2019m sorry, I accidentally <BLANK>"
let current_prompt_id = -1;
let current_options = ["Funny Answer", "Very Funny Answer", "Lustig Lustig"]
let my_player_name = ""


let all_divs = []

function reset_values() {
    let current_prompt = ""
    let current_prompt_id = -1;
    let current_options = []
    let my_player_name = ""
}

function set_all_divs() {


    all_divs = document.getElementsByTagName("div");


}

function set_active_screen(div_id) {

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

    let list = document.getElementById("vote_options")

    let new_list_of_options = ""

    for (let i = 0; i < current_options.length; i++) {
        let line_to_attach = "<li id='vote_option_" + (i + 1) + "'>" + current_options[i] + "</li>"

        //<li id="vote_option_1">Option 1</li>
        new_list_of_options += line_to_attach;

    }
    list.innerHTML = new_list_of_options;

}

function display_prompt(prompt) {

    // TO DO clean it up
    document.getElementsByClassName("current_prompt")[0].innerText = current_prompt
    document.getElementsByClassName("current_prompt")[1].innerText = current_prompt

}

// IE does not know about the target attribute. It looks for srcElement
// This function will get the event target in a browser-compatible way
function getEventTarget(e) {
    e = e || window.event;
    return e.target || e.srcElement;
}


function get_player_ip_address() {
    return "placeholderIp";
}

function update_displayed_player_name() {
    document.querySelector("#display_player_name > h3").innerText = "" + my_player_name
}

function handle_player_connect(player_name, player_ip_address) {
    my_player_name = player_name
    update_displayed_player_name()
    console.log(player_name, player_ip_address)
        // connect_to_socket('http://192.168.0.119:25565', player_name)
    connect_to_socket('http://91.64.111.47:25565', player_name)

}

function handle_prompt_answer(prompt_answer) {

    console.log(prompt_answer)
    send_prompt_answer(prompt_answer, current_prompt_id, my_player_name)

}

function handle_player_vote(option) {

    console.log(option)

    let options_id = parseInt(option.slice(-1))
    options_id--

    send_player_vote(options_id, current_prompt_id, my_player_name)

}

window.onload = () => {


    console.log("JS start now")

    set_all_divs()
    set_active_screen('player_connect')

    document.querySelector("#player_name_submit").onclick = () => {

        console.log("Player Name Submit Button pressed")

        let player_name = document.querySelector("#player_name").value
        let player_ip_address = get_player_ip_address()

        if (player_name == "") {
            // handle empty string

        } else {
            handle_player_connect(player_name, player_ip_address)
            set_active_screen('player_wait')
        }
    }

    document.querySelector("#prompt_answer_submit").onclick = () => {
        // Prompt Answer Submit Button pressed
        let prompt_answer = document.querySelector("#prompt_answer").value

        if (prompt_answer == "") {
            // handle empty string
        } else {
            handle_prompt_answer(prompt_answer) //sends answer with metadata to socket server
            set_active_screen('player_wait')
        }
    }

    // https://stackoverflow.com/questions/5116929/get-clicked-li-from-ul-onclick

    document.querySelector("#player_vote_prompt > ul").onclick = (event) => {
        console.log("Player has voted for something")

        let target = getEventTarget(event)
        handle_player_vote(target.id)
        set_active_screen('player_wait')

    }

}