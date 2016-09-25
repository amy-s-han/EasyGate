$("#flightNumberUpdate").click(function() {
	socket.emit('flight_info_query', { flightnumber: $("#flightNumberUpdate").val() });
});


socket.on('flight_info_query_fail', function(msg) {
    console.log(msg.error);
});
