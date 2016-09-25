var socket = io.connect('http://' + document.domain + ':' + location.port);


$("#flightNumberUpdate").click(function() {
	socket.emit('flight_info_query', { flightnumber: $("#flight_number").val() } );
});


$(document).keypress(function(e) {
    if(e.which == 13) {
        socket.emit("initiate_scan", { "a": "b"});
    }
});

var passengers = 1;
socket.on('passenger_information_update', function(pass) {
    $("#passenger_name").val(pass.name);
    $("#passenger_destination").val(pass.destination);
    $("#passenger_class").val(pass.class);
    $("#passenger_seat").val(pass.seat);
    
    $("#passengers_boarded").val(passengers + "/112");
    passengers++;
});


socket.on('new_overhead_volume', function(percent) {
    value = percent.toFixed(0);
    $("#progressBarText").text(value);
    $("#progressBar").css({width: value + "%"});
});

socket.on('updated_luggage_count', function(counts) {
    $("#suitcase").val(counts.suitcases);
    $("#bag").val(counts.bags);
});



function str_pad_left(string,pad,length) {
    return (new Array(length+1).join(pad)+string).slice(-length);
}

var seconds = 1;
var timer = setInterval(function() {
    minutes = Math.floor(seconds / 60);
    secs = seconds % 60;
    timer = minutes + ":" + str_pad_left(secs, '0', 2);
    $("#time_elapsed").val(timer);
    seconds++;
}, 1000);
