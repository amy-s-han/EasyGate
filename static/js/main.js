$("#flightNumberUpdate").click(function() {
	socket.emit('flight_info_query', { flightnumber: $("#flightNumberUpdate").val() } );
});