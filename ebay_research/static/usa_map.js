var sizeRef = 2. * Math.max.apply(null, df['itemId']) / (40. ** 2);

var data = [{
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


var layout = {
        margin:{r:25, t:25, l:25, b:25},
        geo:{scope:'usa',
             projection:{type:'albers usa'},
             showland:true,
             showlakes:false,
             landcolor:"rgb(240, 248, 255)",
             subunitcolor:"rgb(0, 0, 0)",
             countrycolor:"rgb(202, 225, 255)",
             countrywidth:0.5,
             subunitwidth:0.5}
    };

Plotly.newPlot('usaMAP', data, layout, {"displayModeBar": false});