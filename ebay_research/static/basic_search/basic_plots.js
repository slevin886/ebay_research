// Data passed to script as df_type (precompiled list of traces) & df_hist (list of prices)

// Price by Type of Listing

var layout = {'yaxis': {'title': 'Item Price', 'tickprefix': '$'},
              'xaxis': {'showticklabels': false,},
              'height': 350, 'width': 450,
              'margin': {'t': 10},
              'legend': {"orientation": "h"}};

Plotly.newPlot('dfTypePlot', df_type, layout, {"displayModeBar": false});


// Price Histogram
var maxPrice = Math.max.apply(null, df_hist);

var data2 = [{'x': df_hist, 'type': 'histogram',
             'xbins': {'start': 0, 'size': Math.round(maxPrice / 25)},
             'marker': {'line': {'color': 'black', 'width': 2}}
             }];

var layout2 =  {'xaxis': {'title': 'Item Price', 'tickprefix': '$'},
                'yaxis': {'title': '# of Items'},
                'margin': {'t': 0},
                'height': 350, 'width': 450,
                };

Plotly.newPlot('histData', data2, layout2, {"displayModeBar": false});


// Pie Listing Chart

var layout3 = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
              'legend': {"orientation": "h"},
               'height': 350, 'width': 450};

Plotly.newPlot('dfPie', df_pie, layout3, {"displayModeBar": false});


// Sunburst Plot

var layout4 = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
               'height': 350,
                'width': 450};

Plotly.newPlot('sunBurst', make_sunburst, layout4, {"displayModeBar": false});