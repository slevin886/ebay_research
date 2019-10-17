
const spinOptions = {
  lines: 13,
  length: 38,
  width: 17,
  radius: 45,
  scale: 0.2,
  left: '0%',
  color: ['#ff0000', '#000000'],
};

async function pullData() {
  const formData = new FormData(mainForm);
  let firstPull = true;
  let errorMessage = '';
  let showError = false;
  let maxPages = formData.get('items_to_pull');
  let searchID;
  const target = document.getElementById('loading_spinner');
  let spinner = new Spinner(spinOptions).spin(target);
  formData.append('pageNumber', '1');
  formData.append('first_pull', 'true');
  formData.append('last_pull', 'false');
  formData.append('max_pages', maxPages.toString());

  for (let i = 1; i <= maxPages; i++) {

    formData.set('pageNumber', i.toString());

    if (i === parseInt(maxPages)) {
      formData.set('last_pull', 'true')
    }
    await axios.post(
      '/get_data',
      formData,
      {
        headers: {
          'Content-type': 'multipart/form-data',
        }
      }
    )
      .then((res) => {
        const myData = res.data;
        const stats = myData['stats'];
        if (firstPull) {
          firstPull = false;
          formData.set('first_pull', 'false');
          searchID = myData['search_id'];

          document.getElementById('hideDashBoard').style.display = 'block';
          document.getElementById("total_entries").innerHTML = stats['total_entries'];
          document.getElementById('search_url').href = myData['search_url'];

          let availablePages = Math.ceil(stats['total_entries'] / 100);

          if (availablePages < maxPages) {
            maxPages = availablePages;
          }

          if (stats['largest_cat_name'] != null) {
            document.getElementById("largest_cat_name").innerHTML = stats['largest_cat_name'];
            document.getElementById("largest_cat_count").innerHTML = stats['largest_cat_count'];
            document.getElementById("largest_sub_name").innerHTML = stats['largest_sub_name'];
            document.getElementById("largest_sub_count").innerHTML = stats['largest_sub_count'];
          }

          if (myData.sunburst_plot != null) {
            document.getElementById('hideSunBurst').style.display = 'block';
            drawSunBurst(myData.sunburst_plot);
          }
        }

        document.getElementById("returned_count").innerHTML = stats['returned_count'];
        document.getElementById("top_rated_listing").innerHTML = stats['top_rated_listing'];
        document.getElementById("top_seller").innerHTML = stats['top_seller'];
        document.getElementById("top_seller_count").innerHTML = stats['top_seller_count'];
        document.getElementById("top_rated_percent").innerHTML = stats['top_rated_percent'];
        document.getElementById("avg_price").innerHTML = stats['avg_price'];
        document.getElementById("median_price").innerHTML = stats['median_price'];
        document.getElementById("min_price").innerHTML = stats['min_price'];
        document.getElementById("max_price").innerHTML = stats['max_price'];
        document.getElementById("avg_shipping_price").innerHTML = stats['avg_shipping_price'];
        document.getElementById("total_watch_count").innerHTML = stats['total_watch_count'];

        drawFigures(myData.df_type, myData.hist_plot, myData.map_plot, myData.tab_data,
          myData.df_pie, myData.df_seller, myData.df_length);
        drawTable(myData.tab_data);
      })
      .catch((error) => {
          errorMessage = error.response.data;
          showError = true;
        }
      );
    if (showError) {
      let errorNode = document.createElement('div');
      errorNode.setAttribute('class', 'alert alert-danger alert-dismissible fade show');
      errorNode.innerHTML = `
          <span>${errorMessage}</span>
          <button type="button" class="close" data-dismiss="alert" aria-label="Close">
              <span aria-hidden="true">&times;</span>
          </button>
      `;
      document.getElementById('top_search_page').prepend(errorNode);
      spinner.stop();
      break
    }
  }
  spinner.stop();
}


const commonLayout = {'plot_bgcolor': '#F8F8F8', 'paper_bgcolor':'#F8F8F8', 'hovermode': 'closest',
  'font': {'family': 'Helvetica Neue'}, 'height': 350};
// 'height': 350, 'width': 450,
function drawFigures(df_type, hist_plot, map_plot, tab_data, df_pie, df_seller, df_length) {

  // Price by Type of Listing
  const layout = {'yaxis': {'title': 'Item Price', 'tickprefix': '$', 'type': 'log'},
    'xaxis': {'showticklabels': false,},
    'margin': {'t': 10}, 'legend': {"orientation": "h"}, ...commonLayout};

  Plotly.newPlot('dfTypePlot', df_type, layout, {"displayModeBar": false});


  // Price Histogram
  // let maxPrice = Math.max.apply(null, hist_plot);
  hist_plot.sort();
  let len = hist_plot.length;
  let per95 = Math.floor(len * 0.95) - 1;
  let data2 = [{'x': hist_plot, 'type': 'histogram',
               'xbins': {'start': 0, 'size': Math.round(hist_plot[per95] / 50)},
               'marker': {'line': {'color': 'black', 'width': 2}}
               }];

  let layout2 =  {'xaxis': {'title': 'Item Price', 'tickprefix': '$',},
                  'yaxis': {'title': '# of Items', 'type': 'log',},
                  'margin': {'t': 10}, ...commonLayout};

  Plotly.newPlot('histData', data2, layout2, {"displayModeBar": false});


  // Pie Listing Chart

  const layout3 = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
                'legend': {"orientation": "h"}, ...commonLayout};

  Plotly.newPlot('dfPie', df_pie, layout3, {"displayModeBar": false});

  // USA MAP PLOT
  let sizeRef = 2. * Math.max.apply(null, map_plot['itemId']) / (Math.pow(40., 2));

  let dataMap = [{
          type:'scattergeo',
          locationmode: 'USA-states',
          lon: map_plot['lng'],
          lat: map_plot['lat'],
          text: map_plot['text'],
          mode: 'markers',
          hoverinfo: 'text',
          marker:{size:map_plot['itemId'],
                  sizemode:'area',
                  sizeref: sizeRef,
                  sizemin: 4,
                  opacity:0.8,
                  autocolorscale:true,
                  line: {width: 1, color:'rgba(102, 102, 102)'},
                  cmin: 0,
                  color: map_plot['itemId'],
                  cmax: Math.max.apply(null, map_plot['itemId'])}
          }];


  const layout5 = {
          'margin': {'r': 0, 't': 0, 'l': 0, 'b': 0},
          'geo': {'scope': 'usa',
               'projection': {'type': 'albers usa'},
               'showland': true,
               'showlakes': false,
               'landcolor': "rgb(240, 248, 255)",
               'bgcolor': '#F8F8F8',
               'subunitcolor': "rgb(0, 0, 0)",
               'countrycolor': "rgb(202, 225, 255)",
               'countrywidth': 0.5,
               'subunitwidth': 0.5}, ...commonLayout
      };

  Plotly.newPlot('usaMAP', dataMap, layout5, {"displayModeBar": false});


  // Seller bar plot

  const layout7 = {'margin': {'t': 10}, 'xaxis': {'automargin': true, 'tickangle': 45},
                   'yaxis': {'title': '# of listed items'}, ...commonLayout};

  Plotly.newPlot('sellerBar', df_seller, layout7, {"displayModeBar": false});

  // Time Available Plot

  const layoutLengthBar = {
    'yaxis': {'title': '# of Items'},
    'xaxis': {'title': '# of Days of Available<br>(End Date - Start Date)'},
    ...commonLayout
  };

  Plotly.newPlot('lengthBar', df_length, layoutLengthBar, {"displayModeBar": false});
}

function drawSunBurst(make_sunburst) {
  let layout = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10}, ...commonLayout};
  Plotly.newPlot('sunBurst', make_sunburst, layout, {"displayModeBar": false});
}



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


function drawTable(tab_data) {
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