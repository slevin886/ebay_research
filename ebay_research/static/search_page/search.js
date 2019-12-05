// TODO: undefined: popping up still as the warning message...
import {
  plotPriceByListing, plotPieListing, plotPriceBoxPlot, plotPriceHistogram,
  plotSellerMap, plotSunBurst, plotTopSellers,
} from './plot_functions.js';

import {categoryInitiation} from "./category_ids.js";

import {drawTable} from "./table_function.js";

let alertDiv = document.getElementById('js_alert');
let messageDiv = document.getElementById('alert_message');
const plotSelection = document.getElementById('plotOptions');
const plotSelectOptions = document.getElementsByClassName('search_plots');
const logButtonYaxis = document.getElementById('logButtonYaxis');
const logButtonXaxis = document.getElementById('logButtonXaxis');
const hideDashBoard = document.getElementById('hideDashBoard');

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

function resetPlotOptionVisibility(){
    let i;
    for (i = 0; i < plotSelectOptions.length; i++) {
        plotSelectOptions[i].style.display = "block";
    }
}

let plottingData;

async function pullAsync() {
  hideDashBoard.style.display = 'none';
  document.getElementById('searchButton').disabled = true;
  let formData = new FormData(mainForm);
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
      let myData = res.data;
      let stats = myData.stats;
      plottingData = myData;
      resetPlotOptionVisibility();
      document.getElementById('search_url').href = myData.search_url;
      Object.keys(stats).forEach(key => {
        try {
          document.getElementById(key).innerHTML = stats[key];
        } catch (e) {
          console.log(e);
        }
      });
      drawPlot();
      hideDashBoard.style.display = 'block';  // has to be before drawTable or does not render
      drawTable(myData.tab_data);
    })
    .catch((error) => {
      hideDashBoard.style.display = 'none';
      if (error.response){
        messageDiv.innerText = error.response.data['message'];
      } else {
        console.log(error);
        messageDiv.innerText = 'Whoops! Something went wrong, please try again!';
      }
      alertDiv.style.display = 'block';
      alertDiv.classList.add('show');
      alertDiv.classList.add('alert-danger');
      window.scrollTo(0, 0);
    });
  spinner.stop();
  document.getElementById('searchButton').disabled = false;
  }




function changeLog(axis){
    const switcher = {'log': 'linear', 'linear': 'log'};
    let gd = document.getElementById('plotLocation');
    let newValue = switcher[gd.layout[axis].type];
    let option = axis + '.type';
    let update = {};
    update[option] = newValue;
    Plotly.relayout('plotLocation', update)
  }



  function drawPlot(){
    logButtonYaxis.style.display = 'none';
    logButtonXaxis.style.display = 'none';
    let selection = plotSelection.options[plotSelection.selectedIndex].value;
    for (let option in plottingData) {
      if (!plottingData[option]) {
        document.getElementById(option).style.display = 'none';
        if (option === selection){
          selection = 'df_seller';
        }
      }
    }
    let plot = plotKeys[selection](plottingData[selection]);
    Plotly.newPlot('plotLocation', plot['data'], plot['layout'], {"displayModeBar": false});
  }


window.onload = function () {
  document.getElementById('searchButton').addEventListener('click', pullAsync);
  logButtonYaxis.addEventListener('click',
    function() {changeLog('yaxis');}, false);
  logButtonXaxis.addEventListener('click',
    function() {changeLog('xaxis')}, false);
  plotSelection.addEventListener('change', drawPlot);
  categoryInitiation()
};
