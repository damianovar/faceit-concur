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