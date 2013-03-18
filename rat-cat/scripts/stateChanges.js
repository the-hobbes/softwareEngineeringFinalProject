/*
 * Created 14MAR2013 
 * Authors:
 * 	Ethan
 *
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
	//alert('initialState');

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
		// console.log(currentState);
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
	        state = handleState(response);      
	    });

	    // callback handler that will be called on failure
	    requestDeck.fail(function (jqXHR, textStatus, errorThrown){
	        // log the error to the console
	        console.error(
	            "The following error occured: "+
	            textStatus + errorThrown
	        );
	    });

		//Remove the glow from both glowing pieces in this state
		$('#deck').removeClass('glowing');
		$('#discardPile').removeClass('glowing');
	});


	return state;
}


/*waitingForPCard: This function causes the board to update to the right glowing state
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function waitingForPCard(state){
	alert(' stateChange.js : waitingForPCard state');
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
	alert('HAL state');
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
	alert('playerChoice state');
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
	alert('draw2PlayerChoice state');
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