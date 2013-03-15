/*
 * Created 14MAR2013 
 * Authors:
 * 	Ethan
 *
 */

/*
 *renderState: This function takes the state of the game and it's transitioning state and 
 *			merges the two into the new state of the game. This functions depends on the 
 *			following ID's being present on the game.html page: 
 *				opCard1,opCard2,opCard3,opCard4,discardPile,deck,currentCard,knockButton,playerCard1,playerCard2,playerCard3,playerCard4
 *	state: The JSON representative of the game board, this is a JSON
 *		   object which has the following high level pairs:
 *		   { "Deck" : {}, "Discard" : {}, "CompCard" : {}, "PlayCard" : {},
 * 			 "DisplayCard" : {}, "KnockState" : 0 | 1, "State" : "state specified by specs" }			 
 *	returns: the new state of the game
 */
 function renderState(oldState,newState){
 	if(oldState == null){
 		//Initializing the game so the newState is correct
 		return newState;	
 	}
 	alert(oldState["KnockState"]);





 }