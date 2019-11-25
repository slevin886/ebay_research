import {
  plotPriceByListing, plotPieListing, plotPriceBoxPlot, plotPriceHistogram,
  plotSellerMap, plotSunBurst, plotTimeAvailable, plotTopSellers,
} from './plot_functions.js';

import {categoryInitiation} from "./category_ids.js";

import {drawTable} from "./table_function.js";

let alertDiv = document.getElementById('js_alert');
let messageDiv = document.getElementById('alert_message');


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
  let maxPages = document.querySelector('input[name="pull_options"]:checked').value;
  let searchID;
  let stopLoop;
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
        if (myData && stats) {
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
              try {
                document.getElementById(key).innerHTML = stats[key];
              } catch (e) {
                console.log(e);
              }
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
        } else {
          stopLoop = true;
        }
      })
      .catch((error) => {
          console.log(error);
          messageDiv.innerText = 'Whoops! Something went wrong, we were unable to complete your search.';
          alertDiv.style.display = 'block';
          alertDiv.classList.add('show');
          alertDiv.classList.add('alert-danger');
          spinner.stop();
          document.getElementById('searchButton').disabled = false;
          stopLoop = true;
        }
      );
    if (stopLoop){
      break;
    }
  }
  spinner.stop();
  document.getElementById('searchButton').disabled = false;
}


window.onload = function () {
  document.getElementById('searchButton').addEventListener('click', pullData);
  categoryInitiation()
};
