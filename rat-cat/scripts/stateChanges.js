/*
 * Created 14MAR2013 
 * Authors:
 * 	Ethan
 *
 * The purpose of this file is to provide the changes to the view upon each change of state. The following functions
 * are defined here:
 *	initialState(state)
 *	waitingForDraw(state)
 *	waitingForPCard
 * 	HAL(state)
 *	playerChoice(state)
 *	draw2PlayerChoice
 *	handleState(state)
 */


/*initialState: This function shows the player their cards for a brief time and then transitions 
 *			to the next state
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function initialState(state){
	console.log('initialState entered');

	//Any fancy animations for shuffling and dealing go here, such as tweening cards from the deck to the players hands

	//Show the player their two outermost cards for a short time:
	$('#playerCard1').css("background-image", 'url(images/cards/smallCards/'+ state.playCard[0].image +'.png)');
	$('#playerCard4').css("background-image", 'url(images/cards/smallCards/'+ state.playCard[3].image +'.png)');

	//The function below fades out the card and then fades it back in with a function callback
	$('#playerCard1').animate({opacity : 0},4000,function(){ $('#playerCard1').animate({opacity : 1},1000)});
	$('#playerCard4').animate({opacity : 0},4000,function(){ $('#playerCard4').animate({opacity : 1},1000)});

	//This function 'hides' the cards again
	setTimeout(function(){
		$('#playerCard1').css("background-image", 'url(images/cards/smallCards/13.png)');
		$('#playerCard4').css("background-image", 'url(images/cards/smallCards/13.png)');
	},5000);

	//No real need for an ajax call we'll just update things here
	state.state = 'waitingForDraw';

	//We need some timing here so that the glow for the next state doesn't happen immediately
	setTimeout(function(){waitingForDraw(state);},5000);

	return state;

}


/*waitingForDraw: This function causes the board to update to the right glowing state
 *			Which means glowing the discard and deck
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function waitingForDraw(state){
	console.log("waitingForDraw state entered");
	//Add glow to whatever the user will interact with
	$('#deck').addClass('glowing');
	$('#discardPile').addClass('glowing');

	//Add Ajax class to things that will be responsive to user input
	$('#deck').addClass('waitingForDrawAJAX');
	$('#discardPile').addClass('waitingForDrawAJAX');

	//This actually causes the glow
	var glow = $('.glowing');
	setInterval(function(){
	    glow.hasClass('glow') ? glow.removeClass('glow') : glow.addClass('glow');
	}, 2000);
	
	
	//Add listeners for clicks that will fire off whatever interaction we need
	//and will also remove the glow

	$('.waitingForDrawAJAX').bind('click',function(){
		//CHANGE: added a player clicks array to track what the player has actually clicked. We will probs need to include
		// this in documentation going forward, and modify our current code to accomodate for it. 
		state.playerClicks.push(this.id);

		//Use ajax to yell over to the server that something has happened

	    var requestDeck = $.ajax({
	        url: "/game",
	        type: 'POST',
			data: JSON.stringify(state),
			contentType: "application/json",
			dataType: 'json'
	    });

	    // callback handler that will be called on success
	    requestDeck.done(function (response, textStatus, jqXHR){
	        console.log('Returned from waitingForDrawAJAX callback');
	        // console.log(response);

	        //Remove the click so we don't send a ajax request to the server while this 
	        //click shouldn't do anything
	    	$('.waitingForDrawAJAX').unbind('click');
			$('.waitingForDrawAJAX').removeClass('waitingForDrawAJAX');
	        state = handleState(response);      
	        renderState(1,state);


	    });

	    // callback handler that will be called on failure
	    requestDeck.fail(function (jqXHR, textStatus, errorThrown){
	        // log the error to the console
	        console.error(
	            "The following error occured: "+
	            textStatus, errorThrown
	        );
	    });

		//Remove the glow from both glowing pieces in this state
		$('#deck').removeClass('glowing');
		$('#discardPile').removeClass('glowing');
		
	});


	return state;
}


/*waitingForPCard: This function causes the board to update to the right glowing state, which is having
 *			each of the players cards glow
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function waitingForPCard(state){
	console.log('waitingForPCard state entered');
	
	//Iterate through each div within playerCards and add the glowing class
	var $divs = $('#playerCards').children('div').each(function(){
		$(this).addClass('glowing');
		$(this).addClass('waitingForPCardAJAX');
	});

	//This code is copy pasted anywhere we need to glow, seems awfully silly, but I can't
	//Seem to put the glowing into a function without it ceasing functioning. Weird.
	//This will be refactored at a later date.
	var glow = $('.glowing');
	setInterval(function(){
	    glow.hasClass('glow') ? glow.removeClass('glow') : glow.addClass('glow');
	}, 2000);

	//Define the AJAX call to the server 
	$('.waitingForPCardAJAX').bind('click',function(){
		//CHANGE: added a player clicks array to track what the player has actually clicked. We will probs need to include
		// this in documentation going forward, and modify our current code to accomodate for it. 
		state.playerClicks.push(this.id);
		//Use ajax to yell over to the server that something has happened

	    var request = $.ajax({
	        url: "/game",
	        type: 'POST',
			data: JSON.stringify(state),
			contentType: "application/json",
			dataType: 'json'
	    });

	    // callback handler that will be called on success
	    request.done(function (response, textStatus, jqXHR){
	        console.log('Returned from waitingForPCardAJAX callback');
	        // console.log(response);

	        //Remove the click so we don't send a ajax request to the server while this 
	        //click shouldn't do anything
	    	$('.waitingForPCardAJAX').unbind('click');
	    	$('.waitingForPCardAJAX').removeClass('waitingForPCardAJAX');
	        state = handleState(response);      
	        renderState(1,state);

	    });

	    // callback handler that will be called on failure
	    request.fail(function (jqXHR, textStatus, errorThrown){
	        // log the error to the console
	        console.error(
	            "The following error occured: "+
	            textStatus, errorThrown
	        );
	    });

		//Remove the glow from player cards
		$('#discardPile').removeClass('glowing');
		var $divs = $('#playerCards').children('div').each(function(){
			$(this).removeClass('glowing');
		
		});
	});

	return state;
}


/*HAL: This function causes the board to update to the right glowing state
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function HAL(state){
	console.log('HAL state entered');
	//This will probably be one of the more crazy handlers, and will have to talk to the server a lot
	//Basically, once it's our turn the server is going to go through the motions and figure out what the
	//hell it's doing, then it will return that state back to us and we'll have to animate the moves of the 
	//AI. Such as, if it selects from the deck then the display card should show up and then move to the 
	//appropriate card in their hand, that way the user knows which card to ask for if they get a swap
	//card and everything. These kind of things are what we're going to have to deal with. We'll have to
	//call renderState a few times, and use proper timing to get this to work right. And we'll use variables
	//to control the timing so everything is relative and we can set it to 0 for quick debugging or stats 
	//getting.
	console.log(state);

	return state;
}

/*playerChoice: This function causes the board to update to the right glowing state
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function playerChoice(state){
	console.log("playerChoice State entered");
	
	//Add glow to the players cards
	$('#discardPile').addClass('glowing');
	$('#discardPile').addClass('playerChoiceAJAX');

	//Iterate through each div within playerCards and add the glowing class
	var $divs = $('#playerCards').children('div').each(function(){
		$(this).addClass('glowing');
		$(this).addClass('playerChoiceAJAX');
	});

	//This code is copy pasted anywhere we need to glow, seems awfully silly, but I can't
	//Seem to put the glowing into a function without it ceasing functioning. Weird.
	//This will be refactored at a later date.
	var glow = $('.glowing');
	setInterval(function(){
	    glow.hasClass('glow') ? glow.removeClass('glow') : glow.addClass('glow');
	}, 2000);


	//Define the AJAX call to the server 
	$('.playerChoiceAJAX').bind('click',function(){
		//CHANGE: added a player clicks array to track what the player has actually clicked. We will probs need to include
		// this in documentation going forward, and modify our current code to accomodate for it. 
		state.playerClicks.push(this.id);
		
		//Use ajax to yell over to the server that something has happened

	    var request = $.ajax({
	        url: "/game",
	        type: 'POST',
			data: JSON.stringify(state),
			contentType: "application/json",
			dataType: 'json'
	    });

	    // callback handler that will be called on success
	    request.done(function (response, textStatus, jqXHR){
	        console.log('Returned from playerChoiceAJAX callback');
	        // console.log(response);

	        //Remove the click so we don't send a ajax request to the server while this 
	        //click shouldn't do anything
	    	$('.playerChoiceAJAX').unbind('click');
	    	$('.playerChoiceAJAX').removeClass('playerChoiceAJAX');
	        state = handleState(response);      
	        renderState(1,state);
	    });

	    // callback handler that will be called on failure
	    request.fail(function (jqXHR, textStatus, errorThrown){
	        // log the error to the console
	        console.error(
	            "The following error occured: "+
	            textStatus, errorThrown
	        );
	    });

		//Remove the glow from discard and player cards
		$('#discardPile').removeClass('glowing');
		var $divs = $('#playerCards').children('div').each(function(){
			$(this).removeClass('glowing');
		
		});
	});


	return state;
}

/*draw2PlayerChoice: This function causes the board to update to the right glowing state
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function draw2PlayerChoice(state){
	console.log('draw2PlayerChoice state entered');
	//In this state, the player has drawn a draw 2 card already, so they have drawn from the deck and are waiting 
	//to select either the discard pile, their card to switch out, or the deck to draw another card.

	//Add glow
	$('#discardPile').addClass('glowing');
	$('#discardPile').addClass('draw2PlayerChoiceAJAX');
	$('#deck').addClass('glowing');
	$('#deck').addClass('draw2PlayerChoiceAJAX');

	//Iterate through each div within playerCards and add the glowing class
	var $divs = $('#playerCards').children('div').each(function(){
		$(this).addClass('glowing');
		$(this).addClass('draw2PlayerChoiceAJAX');
	});

	//This code is copy pasted anywhere we need to glow, seems awfully silly, but I can't
	//Seem to put the glowing into a function without it ceasing functioning. Weird.
	//This will be refactored at a later date.
	var glow = $('.glowing');
	setInterval(function(){
	    glow.hasClass('glow') ? glow.removeClass('glow') : glow.addClass('glow');
	}, 2000);


	//Define the AJAX call to the server 
	$('.draw2PlayerChoiceAJAX').bind('click',function(){
		//CHANGE: added a player clicks array to track what the player has actually clicked. We will probs need to include
		// this in documentation going forward, and modify our current code to accomodate for it. 
		state.playerClicks.push(this.id);
		
		//Use ajax to yell over to the server that something has happened

	    var request = $.ajax({
	        url: "/game",
	        type: 'POST',
			data: JSON.stringify(state),
			contentType: "application/json",
			dataType: 'json'
	    });

	    // callback handler that will be called on success
	    request.done(function (response, textStatus, jqXHR){
	        console.log('Returned from draw2PlayerChoiceAJAX callback');
	        // console.log(response);

	        //Remove the click so we don't send a ajax request to the server while this 
	        //click shouldn't do anything
	    	$('.draw2PlayerChoiceAJAX').unbind('click');
	    	$('.draw2PlayerChoiceAJAX').removeClass('draw2PlayerChoiceAJAX');
	        state = handleState(response);      
	        renderState(1,state);

	    });

	    // callback handler that will be called on failure
	    request.fail(function (jqXHR, textStatus, errorThrown){
	        // log the error to the console
	        console.error(
	            "The following error occured: "+
	            textStatus, errorThrown
	        );
	    });

		//Remove the glow from discard and player cards
		$('#discardPile').removeClass('glowing');
		$('#deck').removeClass('glowing');
		var $divs = $('#playerCards').children('div').each(function(){
			$(this).removeClass('glowing');
		
		});
	});
	return state;
}

/*handleState: This function passes the state through a switch statement and calls the proper rendering function
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function handleState(state){
	switch( state.state){
		case 'waitingForDraw':
			return waitingForDraw(state);
		case 'waitingForPCard':
			return waitingForPCard(state);
		case 'HAL':
			return HAL(state);
		case 'playerChoice':
			return playerChoice(state);
		case 'draw2PlayerChoice':
			return draw2PlayerChoice(state);
		case 'initial':
			return initialState(state);
		default:
			return state;
	}
}