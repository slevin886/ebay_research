import {
  plotPriceByListing, plotPieListing, plotPriceBoxPlot, plotPriceHistogram,
  plotSellerMap, plotSunBurst, plotTimeAvailable, plotTopSellers
} from './plot_functions.js';

// options for loading spinner
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
  // ensure button is disabled while searching
  document.getElementById('searchButton').disabled = true;
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
            plotSunBurst(myData.sunburst_plot);
          }
          // Shouldn't happen any more, but sometimes bad zip code data
          if (myData.map_plot != null) {
            document.getElementById('hideMap').style.display = 'block';
          }

        }
        // Setting main statistics on page
        Object.keys(stats).forEach(key => {
            document.getElementById(key).innerHTML = stats[key];
          }
        );

        plotPriceByListing(myData.df_type);
        plotPieListing(myData.df_pie);
        plotTopSellers(myData.df_seller);
        plotPriceBoxPlot(myData.df_box);
        plotPriceHistogram(myData.hist_plot);
        plotSellerMap(myData.map_plot);
        plotTimeAvailable(myData.df_length);
        plotTopSellers(myData.df_seller);
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
      document.getElementById('top_search_page').appendChild(errorNode);
      spinner.stop();
      break
    }
  }
  spinner.stop();
  document.getElementById('searchButton').disabled = false;
}

window.onload = function () {
  document.getElementById('searchButton').addEventListener('click', pullData)
};

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