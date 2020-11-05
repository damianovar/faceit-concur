/* $("form[name=signup_form").submit(function (e) {
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();


  $.ajax9({
    url: "/user/signup",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (resp) {
      window.location.href = "/templates/index/";
      console.log(resp);
    },
    error: function (resp) {
      console.log(resp);
    }
  });
  e.preventDefault();
}); */