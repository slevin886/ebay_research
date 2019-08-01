
var table = new Tabulator("#tab_location", {
	data:tab_data,           //load row data from array
	layout:"responsiveLayout",      //fit columns to width of table
//	responsiveLayout:"hide",  //hide columns that dont fit on the table
	tooltips:true,            //show tool tips on cells
	addRowPos:"top",          //when adding a new row, add it to the top of the table
	history:true,             //allow undo and redo actions on the table
	pagination:"local",       //paginate the data
	paginationSize:3,         //allow 7 rows per page of data
	movableColumns:true,      //allow column order to be changed
	resizableRows:true,       //allow row order to be changed
	headerFilterPlaceholder: "search/filter...",
	columns:[                 //define the table columns
	    {formatter:"rownum"},
		{title:"Current Price", field:"currentPrice_value", formatter:"money", formatterParams:{symbol: "$"}},
		{title:"Title", field:"title", formatter:"textarea", width:150, headerFilter:"input"},
		{title:"Image", field:"galleryURL", formatter:"image", width:150},
		{title:"Location", field:"location", headerFilter:"input"},
		{title:"Bid Count", field:"bidCount"},
		{title:"Start Time", field:"startTime"},
		{title:"End Time", field:"endTime"},
		{title:"Listing Type", field:"listingType", headerFilter:"input"},
		{title:"View Item on eBay", field:"viewItemURL", formatter:"link", width:200},
	],
});