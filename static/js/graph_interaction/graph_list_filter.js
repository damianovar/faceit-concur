

function graph_list_filter(){

  // Declare variables
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById('graph_list_searchbar');
  filter = input.value.toUpperCase();
  ul = document.getElementById("graph_list");
  li = ul.getElementsByTagName('li');

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("h2")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }

}