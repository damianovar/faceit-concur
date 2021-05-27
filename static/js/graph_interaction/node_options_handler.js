function query_for_question() {
    console.log('Hahaha:');
}

function node_click(properties) {
    node_options = document.getElementById("node_options");
    node_options.style.top_margin = "20%";
    var ids = properties.nodes;
    var clickedNodes = nodes.get(ids);

    if (clickedNodes.length != 0){
        node_options.style.display = "initial";
        console.log('clicked nodes:', clickedNodes);
        var name = capitalize_first_letter(clickedNodes[0].id);
        node_options.querySelector("#node_options_title").innerHTML = name;
        
    }
    else{
        node_options.style.display = "none";
    }

}

function capitalize_first_letter(word){
    return word.charAt(0).toUpperCase() + word.slice(1)
}
