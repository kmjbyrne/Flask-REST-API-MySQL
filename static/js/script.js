
$(document).ready(function(){
	console.log("HERE");
	$(document).on('click', 'button', function(){
  		getTableData($(this).attr('id'));
	});

	$.getJSON({
	  	type: 'GET',
	 	url: '/api/table/list',
	  	contentType: 'application/vnd.collection+json',
	  	dataType: 'json',
	  	success: function(getdata) 
	  	{
	  		var length = getdata.collection.items.length;
	  		for(var i = 0; i < length; i++)
	  		{
	  			var link = getdata.collection.items[i].href;
	  			var div = "<div class = inner id = "+i+"></div>";
	  			var button_content = ("API LINK - " + link);
	  			var href = "<button id = "+link+">" + button_content + "</button>";
	  			var block = "<h1>" + getdata.collection.items[i].data.table + "</h1>";
	  			$(".container").append($(div));
	  			$("#"+i).append($(href), $(block));
	  		}
	  	}
	});
});


function getTableData(url){
	$.getJSON({
	  	type: 'GET',
	 	url: url,
	  	contentType: 'application/vnd.collection+json',
	  	dataType: 'json',
	  	success: function(getdata) 
	  	{
	  		var length = getdata.collection.items.length;
	  		for(var i = 0; i < length; i++)
	  		{
	  			var link = getdata.collection.items[i].href;
	  			var div = "<div class = inner id = "+i+"></div>";
	  			var button_content = ("API LINK - " + link);
	  			var href = "<button id = "+link+">" + button_content + "</button>";
	  			var block = "<h1>" + JSON.stringify(getdata.collection.items[i]) + "</h1>";
	  			$(".container").html($(div));
	  			$("#"+i).append($(href), $(block));
	  		}
	  	}
	});
}