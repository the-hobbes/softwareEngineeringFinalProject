function insertAudio(src){
  var embed=document.createElement('object');
  embed.setAttribute('type', 'audio/wav'); //audio/mpeg or audio/wav
  embed.setAttribute('data', src); //sounds/file.(extension)
  embed.setAttribute('enablejavascript', true);
  embed.setAttribute('autostart',true);
  embed.setAttribute('width',0);
  embed.setAttribute('height',0);
  				
	$('#sound').append(embed);

}