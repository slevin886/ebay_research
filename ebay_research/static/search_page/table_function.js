//creates clickable anchor tag for tabulator function
const linkFormatter = function(cell, formatterParams){
	let value = this.sanitizeHTML(cell.getValue()),
	urlPrefix = formatterParams.urlPrefix || "",
	label = this.emptyToSpace(value),
	data;

	if(formatterParams.labelField){
		data = cell.getData();
		label = data[formatterParams.labelField];
	}

	if(formatterParams.label){
		switch(typeof formatterParams.label){
			case "string":
			label = formatterParams.label;
			break;

			case "function":
			label = formatterParams.label(cell);
			break;
		}
	}

	if(formatterParams.urlField){
		data = cell.getData();
		value = data[formatterParams.urlField];
	}

	if(formatterParams.url){
		switch(typeof formatterParams.url){
			case "string":
			value = formatterParams.url;
			break;

			case "function":
			value = formatterParams.url(cell);
			break;
		}
	}

	return "<a href='" + urlPrefix + value + "' target='_blank'>" + label + "</a>";
};


export function drawTable(tab_data) {
	const table = new Tabulator("#tab_location", {
			data: tab_data,           //load row data from array
			layout: "fitColumns",      //fit columns to width of table
			responsiveLayout: "hide",  //hide columns that dont fit on the table
			tooltips: true,            //show tool tips on cells
			initialSort: [{column: "watchCount", dir: "desc"}],
			pagination: "local",       //paginate the data
			paginationSize: 3,         //allow 7 rows per page of data
			movableColumns: false,      //allow column order to be changed
			resizableRows: false,       //allow row order to be changed
			headerFilterPlaceholder: "search/filter...",
			columns: [                 //define the table columns
				{formatter: "rownum"},
				{title: "Price", field: "currentPrice_value", formatter: "money", formatterParams: {symbol: "$"}},
				{title: "Title", field: "title", formatter: "textarea", headerFilter: "input", width: 200,},
				{title: "Image", field: "galleryURL", formatter: "image", width: 200},
				{title: "Watch<br>Count", field: "watchCount"},
				{title: "End Time", field: "endTime", width: 200, formatter: "textarea"},
				{title: "View it!", field: "viewItemURL", formatter: linkFormatter, formatterParams: {'label': 'see on ebay'}},
			],
		}
	)
}
