
//Source:http://darcyclarke.me/development/animate-float-positions-in-jquery-1-5/
(function(){
    var $plugin = jQuery.sub();
    $plugin.fn.animate = function(props, speed, cb){
        if(typeof(speed) == "function")
            cb = speed, speed = 500;
        if(typeof(cb) != "function")
            cb = function(){};
        return $.each(this, function(i, el){
            el = $(el);
            if(props.float && props.float != el.css("float")){
                var elem = el.clone().css(props).insertBefore(el),
                    temp = (props.float == el.css("float")) ? elem.position().left : el.position().left;
                props.marginLeft = elem.position().left;
                elem.remove();
                el.css({float:"left",marginLeft:temp});
            }
            $(this).animate(props, speed, function(){
                $(this).css(props);
                cb();
            });
        });
    };
    
    $(".float.right").bind("click", function(){
        $plugin(this).animate({float:"right"}, 1000); 
    });
    
    $(".float.left").bind("click", function(){
        $plugin(this).animate({float:"left"}, 1000); 
    });

})();

function animateDeckToCurrent(pClicks){
	console.log("animate deck to current");	

	var newElement = $("#deck").clone();
	newElement.appendTo('#deck');
	
	console.log(newElement)
	
	if (pClicks[0] == "deck") {

	    newElement.animate({
	    	marginRight:'700px',
  			opacity:'0.5',
  			top:'+50px'
	     }, "medium",
	     function(){$(this).remove();})
	}    
 console.log("it's making it to the animation");
}

function animateDiscardToCurrent(pClicks){
	console.log("animate discard to current");

	var newElement = $("#discardPile").clone();
	newElement.appendTo('#discardPile');
	
	console.log(newElement);
	
	if (pClicks[0] == "discardPile") {

	    newElement.animate({
	    	marginLeft:'-170px',
  			opacity:'0.5',
  			top:'+20px'
	     }, 900,
	     function(){$(this).remove();})
	}    
 console.log("it's making it to the animation");
}	
function animateP1Discard(pClicks){
	console.log("move playerCard1 to discard and current to 1")

    var newElement = $("#playerCard1").clone();
    newElement.appendTo('#playerCard1');
    
    console.log(newElement);
    if (pClicks[0] == "playerCard1") {

        newElement.animate({
            marginLeft:'-40px',
            top:'-=300px',
            opacity:'0.5',
         }, 900,
         function(){
            $(this).remove();})
    } 

}    
function animateP2Discard(pClicks){
	console.log("move playerCard2 to discard and current to 2")

    var newElement = $("#playerCard2").clone();
    newElement.appendTo('#playerCard2');
    
    console.log(newElement);
    
    if (pClicks[0] == "playerCard2") {

        newElement.animate({
            marginLeft:'-135px',
            top:'-=300px',
            opacity:'0.5',
         }, 900,
         function(){$(this).remove();})
    }    
}
function animateP3Discard(pClicks){
	console.log("move playerCard3 to discard and current to 3")

    var newElement = $("#playerCard3").clone();
    newElement.appendTo('#playerCard3');
    
    console.log(newElement);
    
    if (pClicks[0] == "playerCard3") {

        newElement.animate({
            marginLeft:'-265px',
            top:'-=300px',
            opacity:'0.5',
         }, 900,
         function(){$(this).remove();})
    }    
}
function animateP4Discard(pClicks){
	console.log("move playerCard4 to discard and current to 4")


    var newElement = $("#playerCard4").clone();
    newElement.appendTo('#playerCard4');
    
    console.log(newElement);
    
    if (pClicks[0] == "playerCard4") {

        newElement.animate({
            marginLeft:'-385px',
            top:'-=300px',
            opacity:'0.5',
         }, 900,
         function(){$(this).remove();})
    }
}
function animateCurrentToHand(){
    var newElement = $("#currentCard").clone();
    newElement.appendTo('#currentCard');

    newElement.animate({
        marginLeft:'+500px'
    })



}