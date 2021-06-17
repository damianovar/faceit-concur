var node_info;

function query_for_question(question) {
    let courses = create_course_string(create_list_of_listed_courses());
    let mode = get_graph_mode();
    let url = "/multi_graphviz/" + "complex numbers";
    window.location.href = url;
}

function node_click(properties) {
    node_options = document.getElementById("node_options");
    node_options.style.top_margin = "20%";
    var ids = properties.nodes;
    var clickedNodes = nodes.get(ids);

    if (clickedNodes.length != 0){
        node_info = clickedNodes[0];
        if (node_info.link == undefined || node_info.link == ""){
            document.getElementById("link_querry_button").style.display = "none";
        }
        else{
            document.getElementById("link_querry_button").style.display = "initial";
        }
        node_options.style.display = "initial";
        var name = capitalize_first_letter(clickedNodes[0].id);
        node_options.querySelector("#node_options_title").innerHTML = name;
        
    }
    else{
        node_options.style.display = "none";
    }

}

function redirect_to_link(){
    if (node_info.link != undefined && node_info.link != ""){
        window.open(node_info.link, '_blank').focus()
    }
}

function capitalize_first_letter(word){
    return word.charAt(0).toUpperCase() + word.slice(1)
}


