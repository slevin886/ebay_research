// Data passed to script as df_type (precompiled list of traces) & df_hist (list of prices)

// Price by Type of Listing

const layout = {'yaxis': {'title': 'Item Price', 'tickprefix': '$'},
              'xaxis': {'showticklabels': false,},
              'height': 350, 'width': 450,
              'margin': {'t': 10},
              'plot_bgcolor': '#F8F8F8' , 'paper_bgcolor':'#F8F8F8',
              'legend': {"orientation": "h"}};

Plotly.newPlot('dfTypePlot', df_type, layout, {"displayModeBar": false});


// Price Histogram
var maxPrice = Math.max.apply(null, df_hist);

var data2 = [{'x': df_hist, 'type': 'histogram',
             'xbins': {'start': 0, 'size': Math.round(maxPrice / 25)},
             'marker': {'line': {'color': 'black', 'width': 2}}
             }];

const layout2 =  {'xaxis': {'title': 'Item Price', 'tickprefix': '$'},
                'yaxis': {'title': '# of Items'},
                'margin': {'t': 0},
                'height': 350, 'width': 450,
                'plot_bgcolor': '#F8F8F8' , 'paper_bgcolor':'#F8F8F8'
                };

Plotly.newPlot('histData', data2, layout2, {"displayModeBar": false});


// Pie Listing Chart

const layout3 = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
              'legend': {"orientation": "h"},
              'plot_bgcolor': '#F8F8F8' , 'paper_bgcolor':'#F8F8F8',
              'height': 350, 'width': 450};

Plotly.newPlot('dfPie', df_pie, layout3, {"displayModeBar": false});


// Sunburst Plot

// const layout4 = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
//                'plot_bgcolor': '#F8F8F8' , 'paper_bgcolor':'#F8F8F8',
//                'height': 350,
//                 'width': 450};
//
// Plotly.newPlot('sunBurst', make_sunburst, layout4, {"displayModeBar": false});


// USA MAP PLOT

var sizeRef = 2. * Math.max.apply(null, df['itemId']) / (Math.pow(40., 2));

var dataMap = [{
        type:'scattergeo',
        locationmode: 'USA-states',
        lon: df['lng'],
        lat: df['lat'],
        text: df['text'],
        mode: 'markers',
        hoverinfo: 'text',
        marker:{size:df['itemId'],
                sizemode:'area',
                sizeref: sizeRef,
                sizemin: 4,
                opacity:0.8,
                autocolorscale:true,
                line: {width: 1, color:'rgba(102, 102, 102)'},
                cmin: 0,
                color: df['itemId'],
                cmax: Math.max.apply(null, df['itemId'])}
        }];


const layout5 = {
        'plot_bgcolor': '#F8F8F8' , 'paper_bgcolor':'#F8F8F8',
        'margin': {'r': 0, 't': 0, 'l': 0, 'b': 0},
        'height': 350, 'width': 450,
        'geo': {'scope': 'usa',
             'projection': {'type': 'albers usa'},
             'showland': true,
             'showlakes': false,
             'landcolor': "rgb(240, 248, 255)",
             'bgcolor': '#F8F8F8',
             'subunitcolor': "rgb(0, 0, 0)",
             'countrycolor': "rgb(202, 225, 255)",
             'countrywidth': 0.5,
             'subunitwidth': 0.5}
    };

Plotly.newPlot('usaMAP', dataMap, layout5, {"displayModeBar": false});