/*
 * Created 14MAR2013 
 * Authors:
 * 	Ethan, Phelan
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

// globally scoped knock variable
knock = 1;

/*updateKnock: This function is used to switch the value of knock on or off. If the value is on (1), users will be prompted to 
 * 	knock every time their turn ends. If the value is off (0), then they won't be prompted and their turn will pass over to  	
 * 	the AI.
 */
function updateKnock(){
	console.log("got to updateKnock");
	if(knock ==1 ){
		//if on, switch off. make it look like it has been pressed down
		knock = 0;
		var pressMe = $('#knockButton');
		pressMe.removeClass('pressed');
	}
	else{
		// if off, switch on. remove the css that makes it look pressed down
		knock = 1;
		var pressMe = $('#knockButton');
		pressMe.addClass('pressed');
	}
	console.log(knock);
}

function updateKnockState(){
	// knocking logic to update knockstate before the state is Posted
	if(knock == 1){
		//returns a boolean, telling us if they want to knock or not. 
		result = confirm("Would you like to knock? If you don't want to get this prompt, uncheck the knock button.");
		// console.log("the result of that was:");
		// console.log(result);
		if(result == true){
			//if they want to knock, we will update the knockstate to
			return 2;
		}
		else{
			//if they don't want to knock, we will update the knockstate to do nothing.
			return 0;			
		}
	}
	else{
		//otherwise, knockstate isn't checked and we return 0
		return 0;
	}
}

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
	},6000);

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
	state = glowActiveCards(state);

	//Add Ajax class to things that will be responsive to user input
	$('#deck').addClass('waitingForDrawAJAX');
	$('#discardPile').addClass('waitingForDrawAJAX');

	//This actually causes the glow
	var glow = $('.glowing');
	setInterval(function(){
	    glow.hasClass('glow') ? glow.removeClass('glow') : glow.addClass('glow');
	}, 2000);
	


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
		var localClicks = state.playerClicks;
	    
	    // callback handler that will be called on success
	    requestDeck.done(function (response, textStatus, jqXHR){
	        console.log('Returned from waitingForDrawAJAX callback');
	        // console.log(response);
	       	
	        //Remove the click so we don't send a ajax request to the server while this 
	        //click shouldn't do anything
	    	$('.waitingForDrawAJAX').unbind('click');
			$('.waitingForDrawAJAX').removeClass('waitingForDrawAJAX');
	        state = handleState(response);      
	        renderState(1,state,localClicks);
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
	
	//Add the glowing state
	state = glowActiveCards(state);

	//Add the ajax handler
	var $divs = $('#playerCards').children('div').each(function(){
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
		
		var localClicks = state.playerClicks;

	    // callback handler that will be called on success
	    request.done(function (response, textStatus, jqXHR){
	        console.log('Returned from waitingForPCardAJAX callback');
	        // console.log(response);
	        console.log('Phelan: this is the object sent back from the server');
	    	console.log(response);
	        //Remove the click so we don't send a ajax request to the server while this 
	        //click shouldn't do anything
	    	$('.waitingForPCardAJAX').unbind('click');
	    	$('.waitingForPCardAJAX').removeClass('waitingForPCardAJAX');
	        state = handleState(response);      
	        renderState(1,state,localClicks);

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

	console.log('HAL Says');
	console.log(state);

	setTimeout(function(){
		showHalLoader();
	},1000);

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
			        setTimeout(function(){
						hideHalLoader();
					},3000);
			        // hideHalLoader();
			        //We're done with HAL's turn, render the players
			        state = handleState(response);      
			        renderState(1,state,[]);
			    });

			    // callback handler that will be called on failure
			    request.fail(function (jqXHR, textStatus, errorThrown){
			        // log the error to the console
			        console.error(
			            "The following error occured: "+
			            textStatus, errorThrown,jqXHR
			        );
			    });

	//state.state = 'waitingForDraw';	
	//state.discardActivity = 1
	//state.deckActivity = 1

	console.log(state)


	state.state = 'waitingForDraw';	
	state = handleState(state);
	renderState(1,state,state.playerClicks);

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
	state = glowActiveCards(state);


	$('#discardPile').addClass('playerChoiceAJAX');


	if(state.displayCard.image == '10'){
		//If we've selected a draw2 card then that means we get to add the call onto the deck
		$('#deck').addClass('playerChoiceAJAX');		
	}

	//Iterate through each div within playerCards and add the glowing class
	var $divs = $('#playerCards').children('div').each(function(){
		if(state.displayCard.image != '10'){
			$(this).addClass('playerChoiceAJAX');	
		}
	});

	//Keep track of cards clicked:
	var pClick = 0;
	var oClick = 0;

	//Add a click pushing function to the opponents cards if we are able to swap:
	if(state.displayCard.image == '12'){
		// alert('SWAPPING TIME');
		var $oDivs = $('#opponentCards').children('div').each(function(){
			$(this).addClass('opSwap');
		});	

		$('.opSwap').bind('click', function(e){
			state.playerClicks.push(this.id);
			//Conditional ajax call here if the player has selected their card already
			oClick = oClick + 1;
			console.log(oClick);

			e.stopImmediatePropagation();
        	e.preventDefault();

			if(oClick > 0 && pClick > 0){
				console.log("hello2");
				state.knockState = updateKnockState();	
				//Fire Ajax
				var request = $.ajax({
			        url: "/game",
			        type: 'POST',
					data: JSON.stringify(state),
					contentType: "application/json",
					dataType: 'json'
			    });
				
				var localClicks = state.playerClicks;

			    // callback handler that will be called on success
			    request.done(function (response, textStatus, jqXHR){
			        console.log('Returned from playerChoiceAJAX callback');
			        // console.log(response);

			        //Remove the click so we don't send a ajax request to the server while this 
			        //click shouldn't do anything
			        $('.opSwap').unbind('click');
			    	$('.playerChoiceAJAX').unbind('click');
			    	$('.playerChoiceAJAX').removeClass('playerChoiceAJAX');
			        state = handleState(response);      
			        renderState(1,state,localClicks);
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
				$('.glowing').removeClass('glowing');	
			}else if(pClick || oClick){
				$('#discardPile').removeClass('glowing');
				$('#discardPile').removeClass('playerChoiceAJAX');
				$('#discardPile').unbind('click');
				
				
				//They clicked but its not time to do ajax, so remove the glow from the cards they clicked
				var $oDivs = $('#opponentCards').children('div').each(function(){
					$(this).removeClass('glowing');
				});	
			}
		});
	}




	//Define the AJAX call to the server 
	$('.playerChoiceAJAX').bind('click',function(e){
		//CHANGE: added a player clicks array to track what the player has actually clicked. We will probs need to include
		// this in documentation going forward, and modify our current code to accomodate for it. 
		state.playerClicks.push(this.id);
		pClick = pClick + 1;
		
		e.stopImmediatePropagation();
        e.preventDefault();

		//Use ajax to yell over to the server that something has happened
		//Normal Player Choice
		if(state.displayCard.image != '12'){

			console.log("hello1");
			state.knockState = updateKnockState();

			// Bring up the loading icon so the user can see we are making progress on their request(this will be closed later in endgame)
			showLoader();
		
		    var request = $.ajax({
		        url: "/game",
		        type: 'POST',
				data: JSON.stringify(state),
				contentType: "application/json",
				dataType: 'json'
		    });

		     var localClicks = 
		    // callback handler that will be called on success
		    request.done(function (response, textStatus, jqXHR){
		        console.log('Returned from playerChoiceAJAX callback');
		        hideLoader();
		        // console.log(response);

		        //Remove the click so we don't send a ajax request to the server while this 
		        //click shouldn't do anything

		    	$('.playerChoiceAJAX').unbind('click');
		    	$('.playerChoiceAJAX').removeClass('playerChoiceAJAX');
		        state = handleState(response);      

		        //close the loading popup
		        renderState(1,state,localClicks);

		    });

		    // callback handler that will be called on failure
		    request.fail(function (jqXHR, textStatus, errorThrown){
		    	hideLoader();
		        // log the error to the console
		        console.error(
		            "The following error occured: "+
		            textStatus, errorThrown
		        );
		    });


			//Remove the glow from discard and player cards
			$('.glowing').removeClass('glowing');
		}else{
			//Swap playerChoice, we need to use the number of clicks
			//so far to say yes we can submit the ajax request.
			if(this.id == "discardPile"){
				state.playerClicks.push(this.id);
				pClick = 0;
				oClick = 0;
				console.log("hello");
				state.knockState = updateKnockState();
				var request = $.ajax({
			        url: "/game",
			        type: 'POST',
					data: JSON.stringify(state),
					contentType: "application/json",
					dataType: 'json'
			    });
			    request.done(function (response, textStatus, jqXHR){
				        console.log('Returned from playerChoiceAJAX callback');
				        // console.log(response);

				        //Remove the click so we don't send a ajax request to the server while this 
				        //click shouldn't do anything
				        $('.opSwap').unbind('click');
				    	$('.playerChoiceAJAX').unbind('click');
				    	$('.playerChoiceAJAX').removeClass('playerChoiceAJAX');
				        state = handleState(response);      
				        renderState(1,state,localClicks);
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
					$('.glowing').removeClass('glowing');	
			}else{
				if(pClick > 0 && oClick > 0){
					console.log("hello3");
					state.knockState = updateKnockState();
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
				        $('.opSwap').unbind('click');
				    	$('.playerChoiceAJAX').unbind('click');
				    	$('.playerChoiceAJAX').removeClass('playerChoiceAJAX');
				        state = handleState(response);      
				        renderState(1,state,localClicks);
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
					$('.glowing').removeClass('glowing');	
				}else if(pClick || oClick){
					$('#discardPile').removeClass('glowing');
					$('#discardPile').removeClass('playerChoiceAJAX');
					$('#discardPile').unbind('click');
					
					var $oDivs = $('#playerCards').children('div').each(function(){
						$(this).removeClass('glowing');
					});	
				}
			}
		}	
	});

	//This code is copy pasted anywhere we need to glow, seems awfully silly, but I can't
	//Seem to put the glowing into a function without it ceasing functioning. Weird.
	//This will be refactored at a later date.
	var glow = $('.glowing');
	setInterval(function(){
	    glow.hasClass('glow') ? glow.removeClass('glow') : glow.addClass('glow');
	}, 2000);


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
	state.deckActivity = 0;
	state = glowActiveCards(state);
	console.log(state)
	renderState(1,state,[null]);

	//Add ajax method
	$('#discardPile').addClass('draw2PlayerChoiceAJAX');
	if(state.draw2Counter != 1){
		$('#deck').removeClass('draw2PlayerChoiceAJAX');	
	}
	//Iterate through each div within playerCards and add the ajax class
	var $divs = $('#playerCards').children('div').each(function(){
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
		//CHANGE: added a player clicks array to track what the player has actually clicked. 
		state.playerClicks.push(this.id);
		

		//Use ajax to yell over to the server that something has happened

	    var request = $.ajax({
	        url: "/game",
	        type: 'POST',
			data: JSON.stringify(state),
			contentType: "application/json",
			dataType: 'json'
	    });
	    var localClicks = state.playerClicks;
	    // callback handler that will be called on success
	    request.done(function (response, textStatus, jqXHR){
	        console.log('Returned from draw2PlayerChoiceAJAX callback');
	        // console.log(response);

	        //Remove the click so we don't send a ajax request to the server while this 
	        //click shouldn't do anything
	    	$('.draw2PlayerChoiceAJAX').unbind('click');
	    	$('.draw2PlayerChoiceAJAX').removeClass('draw2PlayerChoiceAJAX');
	        state = handleState(response);      
	        renderState(1,state,localClicks);

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
		$('.glowing').removeClass('glowing');
		
		
	});
	return state;
}

/*endGame: This function causes the board to update to the end round state.
 * First, it shows a hidden lightbox to interact with the user. Then it sends the state to an interaction function so the 
 * user may decide what to do, depending on whether or not the game is over or the round is over. 
 * note that this lightbox is a jinja snippet called popup.html, which is included in game.html
 */
function endGame(state){
	//render the board visible
	renderState(1,state,[]);
	//close the loading popup
	hideLoader();
	//show the dialog popup
	$('#popupDialog').jqmShow();
	//call the interaction function, passing in the state.
	endGameInteraction(state);
}

/*handleState: This function passes the state through a switch statement and calls the proper rendering function
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function handleState(state){
	switch(state.state){
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
		case 'endGame':
			return endGame(state);
		default:
			return state;
	}
}

/*handleState: This function passes the state and any cards marked active are glown
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }
 *	returns: The updated state
 */
function glowActiveCards(state){
	console.log(state);
	if(state.deckActivity==1){
		$('#deck').addClass('glowing');
	}
	if(state.discardActivity){
		$('#discardPile').addClass('glowing');
	}
	//Iterate through each div within playerCards and add the glowing class
	i=0;
	var $divs = $('#playerCards').children('div').each(function(){
		if(state.playCard[i].active){
			$(this).addClass('glowing');
		}
		i=i+1;
	});

	i=0;
	var $oDivs = $('#opponentCards').children('div').each(function(){
		if(state.compCard[i].active){
			$(this).addClass('glowing');
		}
		i=i+1;
	});	
	return state;
}