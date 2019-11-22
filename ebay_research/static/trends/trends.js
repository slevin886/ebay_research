// TODO: look into why Average Shipping Price not be registering

const recurSelect = document.getElementById('recurring_search');
const trendTopic = document.getElementById('trend_topic');
let plotData;


function createLinePlot(){
  let options = {
  chart: {
    height: window.innerHeight * .65,
    id: 'myChart',
    type: 'area',
    zoom: {enabled: false}
            },
   series: [{data: [], name: ''}],
    dataLabels: {enabled: true},
    stroke: {curve: 'smooth'},
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.3
                },
            },
    xaxis: {type: 'datetime'},
  };
  let chart = new ApexCharts(
    document.querySelector("#trendPlot"),
    options);

  chart.render();
}


const dollarYAxis = {
  title: {text: 'Dollars'},
  labels: {
      formatter: function(value){
          return '$' + value;
        }
      },
  decimalsInFloat: 2,};

const yAxis = {
  decimalsInFloat: 0,};

function drawPlot(){
  let topicValue = trendTopic.options[trendTopic.selectedIndex].value;
  let topicText = trendTopic.options[trendTopic.selectedIndex].innerText;
  const nonDollar = ['top_seller', 'total_entries', 'total_watch_count',
  'top_rated_listing', 'top_rated_percent'];
  let options = {
    yaxis: dollarYAxis,
    title: {text: topicText + ' Trends', align: 'left'}
  };

  if (nonDollar.includes(topicValue)){
    options['yaxis'] = yAxis;
  }

  ApexCharts.exec(
    'myChart',
    'updateSeries',
    [{data: plotData.map(a => ({x: a['date'], y: a[topicValue]})),
      name: topicText}]
    );

  ApexCharts.exec(
    'myChart',
    'updateOptions',
    options,
    );
}


async function getRecurringSearchData() {
  let recurId = recurSelect.options[recurSelect.selectedIndex].value;
  await axios.post(
    '/get_trend_data',
    {'recurring_id': recurId},
  )
    .then((res) => {
      plotData = res.data.data;
      drawPlot();
    })
    .catch((error) => {
      console.log(error);
    });
}



window.onload = function () {
  createLinePlot();
  getRecurringSearchData();
  recurSelect.addEventListener('change', getRecurringSearchData);
  trendTopic.addEventListener('change', drawPlot);
};