import {
  plotPriceByListing, plotPieListing, plotPriceBoxPlot, plotPriceHistogram,
  plotSellerMap, plotSunBurst, plotTopSellers,
} from './plot_functions.js';

import {categoryInitiation} from "./category_ids.js";

import {drawTable} from "./table_function.js";

let alertDiv = document.getElementById('js_alert');
let messageDiv = document.getElementById('alert_message');
const plotSelection = document.getElementById('plotOptions');

// options for loading spinner
const spinOptions = {
  lines: 13,
  length: 38,
  width: 17,
  radius: 45,
  scale: 0.2,
  left: '70%',
  top: '30%',
  color: ['#ff0000', '#000000'],
};


const plotKeys = {
  sunburst_plot: plotSunBurst,
  map_plot: plotSellerMap,
  df_type: plotPriceByListing,
  df_pie: plotPieListing,
  df_seller: plotTopSellers,
  df_box: plotPriceBoxPlot,
  hist_plot: plotPriceHistogram,
};

let plottingData;

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
      plottingData = myData;
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
      drawPlot();
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


  function drawPlot(){
    let selection = plotSelection.options[plotSelection.selectedIndex].value;
    if (!plottingData[selection]){
      selection = 'df_seller';
    }
    let plot = plotKeys[selection](plottingData[selection]);
    Plotly.newPlot('plotLocation', plot['data'], plot['layout'], {"displayModeBar": false});
  }


window.onload = function () {
  document.getElementById('searchButton').addEventListener('click', pullAsync);
  plotSelection.addEventListener('change', drawPlot);
  categoryInitiation()
};
