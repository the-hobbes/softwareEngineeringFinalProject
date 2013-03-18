/*
 * Created 14MAR2013 
 * Authors:
 * 	Ethan
 *
 */

//JavaScript 'includes', if we use ajax the page loads async and we might not have  our dependencies
document.writeln("<script type='text/javascript' src='scripts/stateChanges.js'></script>");

//document.writeln("<script src='//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js'></script>");
//The above is commented out because it produces an error on $('#creditsDialog').jqm(); in game.html

/*
 *renderState: This function takes the state of the game and it's transitioning state and 
 *			merges the two into the new state of the game. This functions depends on the 
 *			following ID's being present on the game.html page: 
 *				opCard1,opCard2,opCard3,opCard4,discardPile,deck,currentCard,knockButton,playerCard1,playerCard2,playerCard3,playerCard4
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "deck" : {}, "discard" : {}, "compCard" : {}, "playCard" : {},
 * 			 "displayCard" : {}, "knockState" : 0 | 1, "state" : "state specified by specs" }			 
 *	returns: the new state of the game
 */
 function renderState(oldState,newState){
 	if(oldState == null){
 		//Initializing the game so the newState is correct
 		//TODO: We need to decide the first state of the game and glow appropriate things
 		
 		//Read each state and put the proper image out for the opponent cards:
 		for(var i=0; i < 4; i++){
 			var imgId = newState.compCard[i].image;
 			if(newState.compCard[i].visible){
 				$('#opCard' + (i + 1)).css("background-image", 'url(' + "images/cards/smallCards/"+ imgId + ".png" + ')' );
 			}else{
 				$('#opCard' + (i + 1)).css("background-image", 'url(images/cards/smallCards/13.png)' );
 			}
 		}

 		//Update the images for the player Cards
 		for(var i=0; i < 4; i++){
 			var imgId = newState.playCard[i].image;
 			if(newState.playCard[i].visible){
 				$('#playerCard' + (i + 1)).css("background-image", 'url(' + "images/cards/smallCards/"+ imgId + ".png" + ')' );	
 			}else{
 				$('#playerCard' + (i + 1)).css("background-image", 'url(images/cards/smallCards/13.png)' );	
 			}
 			
 		}

 		//Show the discard pile card:
 		if(newState.discard[0] == null){
 			$('#discardPile').css("background-image", 'url(images/placeholderCard.png)');
 		}else{
 			$('#discardPile').css("background-image", 'url(images/cards/smallCards/' + newState.discard[0] + '.png)');
 		}

 		//Display either the bottom of a card or a placeholder if we managed to run out of deck cards
 		if(newState.deck[0] == null){
 			$('#deck').css("background-image", 'url(images/placeholderCard.png)');
 		}else{
 			$('#deck').css("background-image", 'url(images/cards/smallCards/13.png)');
 		}

 		//Display whatever the currently displayed card is
 		$('#currentCard').css("background-image", "url(images/cards/" + newState.displayCard.image + ".png)");

 		//The knock state should be 0 because we're not ending the game yet
 		newState.knockState = 0;

 		//Set the initial state
 		newState.state = "initial";

 		//Update the state of the board to show the appropriate state (call stateChange.js function)
 		return handleState(newState);

 	}

 	//If the old state is not null then we really only need to update whatever differs between them.
 	//Start with the computer cards:
 	
 }


