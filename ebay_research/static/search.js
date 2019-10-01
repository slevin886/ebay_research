


function pullData() {
  const formData = new FormData(mainForm);
  formData.append('pageNumber', 1);
  let maxPages = formData['items_to_pull'];
  let firstPull = true;
  for (let i=1; i < maxPages; i++) {
    axios.post(
      '/get_data',
      formData,
      {
        headers: {
          'Content-type': 'multipart/form-data',
        }
      }
    )
      .then((res) => {
        document.getElementById('hideDashBoard').style.display = 'block';
        let myData = res.data;
        let stats = myData['stats'];

        document.getElementById("returned_count").innerHTML = stats['returned_count'];
        document.getElementById("total_entries").innerHTML = stats['total_entries'];
        document.getElementById("top_rated_listing").innerHTML = stats['top_rated_listing'];
        document.getElementById("top_seller").innerHTML = stats['top_seller'];
        document.getElementById("top_seller_count").innerHTML = stats['top_seller_count'];
        document.getElementById("top_rated_percent").innerHTML = stats['top_rated_percent'];
        document.getElementById("avg_price").innerHTML = stats['avg_price'];
        document.getElementById("median_price").innerHTML = stats['median_price'];
        document.getElementById("avg_shipping_price").innerHTML = stats['avg_shipping_price'];
        document.getElementById("total_watch_count").innerHTML = stats['total_watch_count'];
        // TODO: Add conditional logic to check these category counts
        if (firstPull && stats['largest_cat_name'] != null) {
          document.getElementById("largest_cat_name").innerHTML = stats['largest_cat_name'];
          document.getElementById("largest_cat_count").innerHTML = stats['largest_cat_count'];
          document.getElementById("largest_sub_name").innerHTML = stats['largest_sub_name'];
          document.getElementById("largest_sub_count").innerHTML = stats['largest_sub_count'];
        }
        if (myData.sunburst_plot != null && firstPull) {
          document.getElementById('hideSunBurst').style.display = 'block';
          drawSunBurst(myData.sunburst_plot);
        }
        drawFigures(myData.df_type, myData.hist_plot, myData.map_plot, myData.tab_data, myData.df_pie, myData.df_seller);
      })
      .catch((error) => {
        console.log(error);
      }
    )
  }
}


const commonLayout = {'plot_bgcolor': '#F8F8F8', 'paper_bgcolor':'#F8F8F8', 'hovermode': 'closest',
  'font': {'family': 'Helvetica Neue'}, 'height': 350, 'width': 450,};
// Price by Type of Listing


function drawFigures(df_type, hist_plot, map_plot, tab_data, df_pie, df_seller) {
  const layout = {'yaxis': {'title': 'Item Price', 'tickprefix': '$'}, 'xaxis': {'showticklabels': false,},
                'margin': {'t': 10}, 'legend': {"orientation": "h"}, ...commonLayout};

  Plotly.newPlot('dfTypePlot', df_type, layout, {"displayModeBar": false});


  // Price Histogram
  let maxPrice = Math.max.apply(null, hist_plot);

  let data2 = [{'x': hist_plot, 'type': 'histogram',
               'xbins': {'start': 0, 'size': Math.round(maxPrice / 25)},
               'marker': {'line': {'color': 'black', 'width': 2}}
               }];

  let layout2 =  {'xaxis': {'title': 'Item Price', 'tickprefix': '$'},
                  'yaxis': {'title': '# of Items'},
                  'margin': {'t': 10}, ...commonLayout};
  console.log(data2);
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
}

function drawSunBurst(make_sunburst) {
  let layout = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10}, ...commonLayout};
  Plotly.newPlot('sunBurst', make_sunburst, layout, {"displayModeBar": false});
}