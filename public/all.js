var oldData, syncTimer = null;
var user, baristaMode;

var MOCK_MODE, mockData;

function sync() {
	// todo: do actual ajax call here.
	
	if(MOCK_MODE) {
		render(mockData);
	} else {
		$.get('/status', function(data) {
			notify(data);
			oldData = data;
			render(data);
		});
	}
	
	if(syncTimer) clearTimeout(syncTimer);
	syncTimer = setTimeout(sync, 30000);
}

function notify(state) {
	var i, l, order;
	for(i=0, l = state.orders.length; i<l; i+=1) {
		order = state.orders[i];
		if(order.userId == user.id && order.readyAt - state.time < 60000) {
			alert("Your coffee is nearly ready. Go pick it up.");
		}
	}
}

function render(state) {
	"use strict";
	console.log("rendering", $("#orders"));
	var users = {}, orders = state.orders, i, l,
		order, user, orderEl, ordersEl;
	
	for(i=0, l = state.users.length; i<l; i+=1) {
		users[state.users[i].id] = state.users[i];
	}
	
	ordersEl = $("#orders");
	ordersEl.empty();
	
	for(i=0, l = state.orders.length; i<l; i+=1) {
		order = orders[i];
		user = users[order.userId];
		
		orderEl = $("<div class='order'>");
		orderEl.append(
			$("<img class='user'>").
			attr("src", user.photo).
			attr("title", user.name)
		);
		orderEl.append(
			$("<div class='coffee'>").
			addClass(order.type)
		);
		orderEl.append(
			$("<span class='readyIn'>").
			text("Ready in " + (order.readyAt - state.time)/60000 + " minutes")
		);
		
		orderEl.append(
			$("<button class='action cancel'>").
			data("orderId", order.id).
			text('Cancel')
		);
		
		if(baristaMode) {
			orderEl.append(
				$("<button class='action start'>").
				data("orderId", order.id).
				text('Start')
			);
			orderEl.append(
				$("<button class='action ready'>").
				data("orderId", order.id).
				text('Ready')
			);
		}
		
		ordersEl.append(orderEl);
	}
}

$(document).ready(function() {
	"use strict";
	$(document).on('click', 'button.cancel', function(event) {
		var orderId = $(this).data("orderId");
		console.log("Cancelling ", orderId);
		$.post('/orders/' + orderId + '/cancel', {}, function(data) {
			sync();
		});
	});
	
	$(document).on('click', 'button.start', function(event) {
		var orderId = $(this).data("orderId");
		console.log("Start ", orderId);
		$.post('/orders/' + orderId + '/start', {}, function(data) {
			sync();
		});
	});
	
	$(document).on('click', 'button.ready', function(event) {
		var orderId = $(this).data("orderId");
		console.log("Ready ", orderId);
		$.post('/orders/' + orderId + '/ready', {}, function(data) {
			sync();
		});
	});
	
	$(".orderBtn").click(function() {
		var orderObject = { type: $(this).data("coffee") };
		console.log("placing an order for ", orderObject);
		$.post('/orders', orderObject, function(data) {
			sync();
		});
	});
	
	$("#loginBtn").click(function() {
		FB.login(onFbLogin);
	});
	
	sync();
});

function onFbLogin(res) {
	if(res.authResponse) {
		FB.api('/me', function(me) {
			user = {
				id: me.id,
				name: me.name,
				photo: "http://graph.facebook.com/" + me.id + "/picture"
			};
			
			// Sharon's facebook ID is 660127222
			// Aravind's 721318124
			
			if(user.id == "721318124") {
				$("#barista").show();
				baristaMode = true;
			}
			
			console.log("user is", me, user);
			
			
			$.post('/login', user, function() {});
		
			
			$("#userPhoto").attr("src", user.photo);
			$("#userName").text(user.name);
			$("#loginBtn").hide();
			
			sync();
		});
	} else {
		$("#loginBtn").show();
	}
}


window.fbAsyncInit = function() {
	// init the FB JS SDK
	FB.init({
		appId      : '482887038437124', // App ID from the App Dashboard
		status     : true, // check the login status upon init?
		cookie     : true, // set sessions cookies to allow your server to access the session?
		xfbml      : true  // parse XFBML tags on this page?
	});
	
	FB.getLoginStatus(onFbLogin);
	
	// Additional initialization code such as adding Event Listeners goes here

};

// Load the SDK's source Asynchronously
// Note that the debug version is being actively developed and might 
// contain some type checks that are overly strict. 
// Please report such bugs using the bugs tool.
(function(d, debug){
	var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
	if (d.getElementById(id)) {return;}
	js = d.createElement('script'); js.id = id; js.async = true;
	js.src = "//connect.facebook.net/en_US/all" + (debug ? "/debug" : "") + ".js";
	ref.parentNode.insertBefore(js, ref);
}(document, /*debug*/ false));



mockData = {
	time: new Date("2013-03-15T19:22:00"),
	orders: [
		{
			id: "98238749",
			type: "cappuccino",
			userId: "asdfasdf",
			orderedAt: new Date("2013-03-15T19:21:00"),
			startedAt: new Date("2013-03-15T19:21:30"),
			readyAt: new Date("2013-03-15T19:24:00")
		},
		{
			id: "9823439",
			type: "americano",
			userId: "sharon",
			orderedAt: new Date("2013-03-15T19:21:00"),
			startedAt: new Date("2013-03-15T19:21:30"),
			readyAt: new Date("2013-03-15T19:24:00")
		},
		{
			id: "982749",
			type: "latte",
			userId: "asdfasdf",
			orderedAt: new Date("2013-03-15T19:21:00"),
			startedAt: new Date("2013-03-15T19:21:30"),
			readyAt: new Date("2013-03-15T19:24:00")
		}
	],
	users: [
		{
			id: "asdfasdf",
			name: "Asdf Asdf",
			photo: "http://graph.facebook.com/aravind.rs/picture"
		},
		{
			id: "sharon",
			name: "Sharon",
			photo: "http://graph.facebook.com/sharonho89/picture"
		}
	]
};
