// single_graph_button,  multi_relation_graph_button, multi_hierarchies_graph_button

var current_interface = "single_graph_button";

function switch_to_multigraph_interface(desired_interface){
    if (current_interface == desired_interface || desired_interface == "single_graph_button"){
        current_interface="single_graph_button";
    }
    else if (desired_interface =="multi_relation_graph_button"){
        current_interface="multi_relation_graph_button"
    }
    else if (desired_interface == "multi_hierarchies_graph_button"){
        current_interface="multi_hierarchies_graph_button"
    }
    show_interface(current_interface);
    toggle_multigraph_button_color();
    clear_graph_list();
}

function show_interface(desired_interface){
    var all_single_graph_buttons = document.getElementsByClassName('single_graph_button');
    var all_multi_relation_buttons = document.getElementsByClassName('multi_relation_graph_button');
    var all_multi_hierarchies_buttons = document.getElementsByClassName('multi_hierarchies_graph_button');

    if (desired_interface == "single_graph_button"){
        change_display_setting_of_class(all_single_graph_buttons, "initial");
        change_display_setting_of_class(all_multi_relation_buttons, "none")
        change_display_setting_of_class(all_multi_hierarchies_buttons, "none")
    }
    else if (desired_interface == "multi_relation_graph_button"){
        change_display_setting_of_class(all_single_graph_buttons, "none");
        change_display_setting_of_class(all_multi_relation_buttons, "initial")
        change_display_setting_of_class(all_multi_hierarchies_buttons, "none")
    }
    else {
        change_display_setting_of_class(all_single_graph_buttons, "none");
        change_display_setting_of_class(all_multi_relation_buttons, "none")
        change_display_setting_of_class(all_multi_hierarchies_buttons, "initial")
    }
}

function change_display_setting_of_class(css_class, setting){
    for (var i = 0; i < css_class.length; i++){
        css_class[i].style.display = setting;
    }
}
function toggle_multigraph_button_color(){
    relation_button = document.getElementById("select_multigraph_relations");
    hierarcy_button = document.getElementById("select_multigraph_hierarchy");

    if (current_interface == "single_graph_button"){
        relation_button.classList.remove('btn-secondary');
        relation_button.classList.add('btn-primary');

        hierarcy_button.classList.remove('btn-secondary');
        hierarcy_button.classList.add('btn-primary');
    }
    else if (current_interface == "multi_relation_graph_button"){
        relation_button.classList.remove('btn-primary');
        relation_button.classList.add('btn-secondary');

        hierarcy_button.classList.add('btn-primary');
        hierarcy_button.classList.remove('btn-secondary');
    }
    else if (current_interface == "multi_hierarchies_graph_button"){
        hierarcy_button.classList.remove('btn-primary');
        hierarcy_button.classList.add('btn-secondary');

        relation_button.classList.add('btn-primary');
        relation_button.classList.remove('btn-secondary');
    }

}

function add_course_to_graph_list(name, id){
    graph_list = document.getElementById("multigraph_list");
    new_list_item = document.createElement("li");
    new_list_item.id = id;
    text = document.createTextNode(name);
    new_list_item.appendChild(text);

    console.log("list item", new_list_item);

    graph_list.appendChild(new_list_item);


}

function clear_graph_list(){
    graph_list = document.getElementById("multigraph_list");
    graph_list.innerHTML  = '';
}

function create_list_of_listed_courses(){
    var mode = "";
    if (current_interface == "multi_relation_graph_button"){
        mode = "relations";  
    }
    else{
        mode = "hierarchies";
    }

    var list_items = document.getElementById("multigraph_list").getElementsByTagName("li");
    var listed_courses = [];
    for (var i = 0; i < list_items.length; i++){
        listed_courses.push(list_items[i].id);
    }
    return listed_courses
    
}

function create_course_string(listed_courses){
    var course_string = "";
    for (var i = 0; i < listed_courses.length; i++){
        course_string += listed_courses[i] + "-";
    }
    return course_string.slice(0, -1);
}

function get_graph_mode(){
    if (current_interface == "multi_relation_graph_button"){
        return "relations";
    }
    return "hierarchies";
}


function display_multi_graph(){
    if (!mutligraph_list_is_empty()){
        let courses = create_course_string(create_list_of_listed_courses());
        let mode = get_graph_mode();
        let url = "/multi_graphviz/" + courses + "/" + mode;
        window.location.href = url;
    }
}

function mutligraph_list_is_empty(){
    return document.getElementById("multigraph_list").innerHTML.trim() == "";
}