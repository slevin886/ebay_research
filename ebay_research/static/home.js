
var table = new Tabulator("#tab_location", {
	data:tab_data,           //load row data from array
//	layout:"responsiveLayout",      //fit columns to width of table
	responsiveLayout:"hide",  //hide columns that dont fit on the table
	tooltips:true,            //show tool tips on cells
	addRowPos:"top",          //when adding a new row, add it to the top of the table
	history:true,             //allow undo and redo actions on the table
	pagination:"local",       //paginate the data
	paginationSize:7,         //allow 7 rows per page of data
	movableColumns:true,      //allow column order to be changed
	resizableRows:true,       //allow row order to be changed
	initialSort:[             //set the initial sort order of the data
		{column:"currentPrice_value", dir:"asc"}, // TODO PROBABLY WANT TO CHANGE THIS
	],
	columns:[                 //define the table columns
		{title:"Current Price", field:"currentPrice_value", editor:"input"},
		{title:"Title", field:"title"},
		{title:"Location", field:"location"},
		{title:"Bid Count", field:"sellingStatus_bidCount"},
		{title:"Time Left", field:"sellingStatus_timeLeft"},
	],
});