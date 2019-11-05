// Plot functions for search.html

const commonLayout = {
  'plot_bgcolor': '#F8F8F8',
  'paper_bgcolor':'#F8F8F8',
  'hovermode': 'closest',
  'font': {'family': 'Helvetica Neue'},
  'height': 350
};


// PLOTTING FUNCTIONS

export function plotPriceByListing(df_type) {
  const layout = {
    'yaxis': {'title': 'Item Price', 'tickprefix': '$', 'type': 'log'},
    'xaxis': {'showticklabels': false,},
    'margin': {'t': 10}, 'legend': {"orientation": "h"},
    ...commonLayout
  };
  Plotly.newPlot('dfTypePlot', df_type, layout, {"displayModeBar": false});
}


export function plotPriceHistogram(hist_plot) {
  hist_plot.sort();
  const len = hist_plot.length;
  const per95 = Math.floor(len * 0.95) - 1;
  const data = [{'x': hist_plot, 'type': 'histogram',
               'xbins': {'start': 0, 'size': Math.round(hist_plot[per95] / 50)},
               'marker': {'line': {'color': 'black', 'width': 2}}
               }];

  const layout =  {'xaxis': {'title': 'Item Price', 'tickprefix': '$',},
                  'yaxis': {'title': '# of Items', 'type': 'log',},
                  'margin': {'t': 10}, ...commonLayout};

  Plotly.newPlot('histData', data, layout, {"displayModeBar": false});
}


export function plotPieListing(df_pie){
    const layout = {
      'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
      'legend': {"orientation": "h"},
      ...commonLayout
    };

    Plotly.newPlot('dfPie', df_pie, layout, {"displayModeBar": false});
}


export function plotSellerMap(map_plot){
    if (map_plot) {
      let sizeRef = 2. * Math.max.apply(null, map_plot['itemId']) / (Math.pow(40., 2));

      let dataMap = [{
        type: 'scattergeo',
        locationmode: 'USA-states',
        lon: map_plot['lng'],
        lat: map_plot['lat'],
        text: map_plot['text'],
        mode: 'markers',
        hoverinfo: 'text',
        marker: {
          size: map_plot['itemId'],
          sizemode: 'area',
          sizeref: sizeRef,
          sizemin: 4,
          opacity: 0.8,
          autocolorscale: true,
          line: {width: 1, color: 'rgba(102, 102, 102)'},
          cmin: 0,
          color: map_plot['itemId'],
          cmax: Math.max.apply(null, map_plot['itemId'])
        }
      }];


      const layout = {
        'margin': {'r': 0, 't': 0, 'l': 0, 'b': 0},
        'geo': {
          'scope': 'usa',
          'projection': {'type': 'albers usa'},
          'showland': true,
          'showlakes': false,
          'landcolor': "rgb(240, 248, 255)",
          'bgcolor': '#F8F8F8',
          'subunitcolor': "rgb(0, 0, 0)",
          'countrycolor': "rgb(202, 225, 255)",
          'countrywidth': 0.5,
          'subunitwidth': 0.5
        },
        ...commonLayout
      };

      Plotly.newPlot('usaMAP', dataMap, layout, {"displayModeBar": false});
  }

}


export function plotTopSellers(df_seller){
    const layout = {
      'margin': {'t': 10},
      'xaxis': {'automargin': true, 'tickangle': 45},
      'yaxis': {'title': '# of listed items'},
      ...commonLayout};

    Plotly.newPlot('sellerBar', df_seller, layout, {"displayModeBar": false});
}


export function plotTimeAvailable(df_length){
  const layout = {
    'yaxis': {'title': '# of Items'},
    'xaxis': {'title': '# of Days of Available<br>(End Date - Start Date)'},
    ...commonLayout
  };

  Plotly.newPlot('lengthBar', df_length, layout, {"displayModeBar": false});
}


export function plotPriceBoxPlot(df_box){
  const layout = {
    'yaxis': {'type': 'log', 'tickprefix':'$', 'title': 'Price (w/ Log Scaled Axis)'},
    'showlegend': false,
    ...commonLayout
  };
  Plotly.newPlot('boxPrice', df_box, layout, {"displayModeBar": false});
}


export function plotSunBurst(make_sunburst) {
  let layout = {
    'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
    ...commonLayout
  };
  Plotly.newPlot('sunBurst', make_sunburst, layout, {"displayModeBar": false});
}
