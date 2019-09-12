// Sunburst Plot

const layout4 = {'margin': {'t': 10, 'l': 0, 'r': 0, 'b': 10},
               'plot_bgcolor': '#F8F8F8' , 'paper_bgcolor':'#F8F8F8',
                'hovermode': 'closest', 'font': {'family': 'Helvetica Neue'},
               'height': 350,
                'width': 450};

Plotly.newPlot('sunBurst', make_sunburst, layout4, {"displayModeBar": false});