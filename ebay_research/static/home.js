
var table = new Tabulator("#tab_location", {
	data:tab_data,           //load row data from array
	layout:"responsiveLayout",      //fit columns to width of table
//	responsiveLayout:"hide",  //hide columns that dont fit on the table
	tooltips:true,            //show tool tips on cells
	addRowPos:"top",          //when adding a new row, add it to the top of the table
	history:true,             //allow undo and redo actions on the table
	pagination:"local",       //paginate the data
	paginationSize:5,         //allow 7 rows per page of data
	movableColumns:true,      //allow column order to be changed
	resizableRows:true,       //allow row order to be changed
//	initialSort:[{column:"currentPrice_value", dir:"asc"}],
	columns:[                 //define the table columns
	    {formatter:"rownum"},
		{title:"Current Price", field:"currentPrice_value", formatter:"money"},
		{title:"Title", field:"title", formatter:"textarea", width:120},
		{title:"Image", field:"galleryURL", formatter:"image", width:120},
		{title:"Location", field:"location"},
		{title:"Bid Count", field:"sellingStatus_bidCount"},
		{title:"Start Time", field:"listingInfo_startTime", sorter:"date"},
		{title:"End Time", field:"listingInfo_endTime", sorter:"date"},
	],
});