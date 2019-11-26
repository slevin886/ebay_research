import {
  plotPriceByListing, plotPieListing, plotPriceBoxPlot, plotPriceHistogram,
  plotSellerMap, plotSunBurst, plotTopSellers,
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
  left: '10%',
  top: '10%',
  color: ['#ff0000', '#000000'],
};


async function pullAsync() {
  document.getElementById('searchButton').disabled = true;
  const formData = new FormData(mainForm);
  let pagesWanted = document.querySelector('input[name="pull_options"]:checked').value;
  formData.append('pages_wanted', pagesWanted.toString());
  const target = document.getElementById('loading_spinner');
  let spinner = new Spinner(spinOptions).spin(target);
  await axios.post(
      '/get_async_data',
      formData,
      {
        headers: {
          'Content-type': 'multipart/form-data',
        }
      }
    )
    .then((res) => {
      const myData = res.data;
      const stats = myData.stats;
      document.getElementById('hideDashBoard').style.display = 'block';
      document.getElementById('search_url').href = myData.search_url;
      Object.keys(stats).forEach(key => {
        try {
          document.getElementById(key).innerHTML = stats[key];
        } catch (e) {
          console.log(e);
        }
      });
      if (myData.sunburst_plot) {
        document.getElementById('hideSunBurst').style.display = 'block';
        plotSunBurst(myData.sunburst_plot);
      }
      // Shouldn't happen any more, but sometimes bad zip code data
      if (myData.map_plot) {
        document.getElementById('hideMap').style.display = 'block';
        plotSellerMap(myData.map_plot);
      }
      plotPriceByListing(myData.df_type);
      plotPieListing(myData.df_pie);
      plotTopSellers(myData.df_seller);
      plotPriceBoxPlot(myData.df_box);
      plotPriceHistogram(myData.hist_plot);
      plotTopSellers(myData.df_seller);
      drawTable(myData.tab_data);
    })
    .catch((error) => {
      messageDiv.innerText = error.response.data['message'];
      alertDiv.style.display = 'block';
      alertDiv.classList.add('show');
      alertDiv.classList.add('alert-danger');
      window.scrollTo(0, 0);
    });
  spinner.stop();
  document.getElementById('searchButton').disabled = false;
  }


window.onload = function () {
  document.getElementById('searchButton').addEventListener('click', pullAsync);
  categoryInitiation()
};
