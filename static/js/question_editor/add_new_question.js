let multiple_choice_answer_counter = 0;

function increment_multiple_choice_counter(){
    multiple_choice_answer_counter++;
}

function decrement_multiple_choice_counter(){
    multiple_choice_answer_counter--;
}

function display_new_question_form(){
    console.log("We got clicked")
    document.location.href = "/new_question";
    console.log("And it is gone");
    return false;
}

function change_to_correct_question_type_form(){
    var e = document.getElementById("question_type");
    if (e.value == "multiple choice"){
        document.getElementById("multiple_choice_form").style.setProperty("display", "initial");
    }
    else {
        document.getElementById("multiple_choice_form").style.setProperty("display", "none");
    }
}

function remove_item_from_multiple_choice_answer_list(event){
    id = event.srcElement.id;
    answer_list = document.getElementById("multiple_choice_answers_list");
    list_items = answer_list.childNodes;

    nodes_to_remove = []
    for (var i = 0; i < list_items.length; i++){
        if (list_items[i].id == id) {
            nodes_to_remove.push(list_items[i])
        }
    }
    for (var i = 0; i < nodes_to_remove.length; i++){
        answer_list.removeChild(nodes_to_remove[i]);
        decrement_multiple_choice_counter();
    }
}

function testing(){
    console.log("Sup?")
    return false;   
}

function add_answer_to_list(){
    answer_list = document.getElementById("multiple_choice_answers_list");
    answer_field = document.getElementById("multiple_choice_answer");

    // Create new list item
    list_item = document.createElement("li");
    list_item.id = multiple_choice_answer_counter.toString();

    // Create a text div
    text_div = document.createElement("div");
    text_div.style ="float:left; width:70%; margin: 0 0 20px 0";
    text = document.createTextNode(answer_field.value)
    text_div.append(text)

    // Create a delete button
    button_div = document.createElement("div");
    button_div.style =  "float:right; width=20%;";

    button = document.createElement("button")
    button.type = "button"; // Necessary to avoid submitting the form
    button.classList.add("btn");
    button.classList.add("btn-danger");
    button.id = multiple_choice_answer_counter.toString();
    button.innerHTML = "x";
    button.onclick = function(event) {remove_item_from_multiple_choice_answer_list(event);}
    button_div.appendChild(button)
    

    list_item.appendChild(text_div);
    list_item.appendChild(button_div);

    answer_list.appendChild(list_item);
    answer_field.value = "";
    increment_multiple_choice_counter();
}