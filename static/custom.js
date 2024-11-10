$(document).ready(function(){
// variation
$(".choose-size").hide();

// show sizes according to colour
$(".choose-color").on('click',function(){
    var _color=$(this).attr('data-color');
    
    $(".choose-size").hide();
    $(".color"+_color).show();
});
// end
// end

$(".choose-size").hide();

// show sizes according to colour
$(".choose-color").on('click',function(){
    var _color=$(this).attr('data-color');
    
    $(".choose-image").hide();
    $(".color"+_color).show();
});

})