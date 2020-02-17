$(window).scroll(function(){
  if ($(window).scrollTop() >= 62) {
      $('#header').addClass('sticky');
  }
  else {
      $('#header').removeClass('sticky');
  }
});

$(document).ready(function(){
    var url = window.location.href;
  $('.menu a').filter(function() {
      return this.href == url;
  }).addClass('current');


//var modal = document.getElementById('result');
//window.onclick = function(event) {
//if (event.target == modal) {
//modal.style.display = "none";
//}
//}

//$(document.body).click( function(e) {
  //  $('#result').show();
//});


$('#result').click( function() {
  $(this).hide();
});

$('.content').click( function() {
  $('#result').hide();
});

$('#search').click( function() {
  $('#result').show();
});

});

$(document).ready(function(){
  $("#search").keyup(function(){
      var data = $(".search_form").serialize()
      
      $.ajax({
          method:"POST",
          url:"/search_user",
          data: data
      })
      .done(function(res){
          $("#result").html(res);
      })

      console.log(data)
      
  })
});

