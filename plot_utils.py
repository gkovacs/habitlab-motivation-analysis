#!/usr/bin/env python
# md5: 3652bf95530fbf560cd0b9030a8d3523
#!/usr/bin/env python
# coding: utf-8



import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)



def plot_data(data, **kwargs):
  title = kwargs.get('title')
  xlabel = kwargs.get('xlabel')
  ylabel = kwargs.get('ylabel')
  
  layout = go.Layout()
  if title is not None:
    layout.title = go.layout.Title(text = title)
  if xlabel is not None:
    layout.xaxis = go.layout.XAxis(title = xlabel)
  if ylabel is not None:
    layout.yaxis = go.layout.YAxis(title = ylabel)
  fig = go.Figure(data=data, layout=layout)
  iplot(fig)

def plot_histogram(x_values, **kwargs):
  data = [go.Histogram(x=x_values)]
  plot_data(data, **kwargs)

def plot_points(points, **kwargs):
  data = [go.Scatter(x=[x for x,y in points], y=[y for x,y in points])]
  plot_data(data, **kwargs)

def plot_several_points(points_list, **kwargs):
  data = []
  for label,points in points_list:
    data.append(go.Scatter(x=[x for x,y in points], y=[y for x,y in points], name=label))
  plot_data(data, **kwargs)

def plot_bar(label_with_value_list, **kwargs):
  labels = [y for x,y in label_with_value_list]
  remap_labels = kwargs.get('remap_labels')
  if remap_labels is not None:
    labels = [remap_labels.get(x, x) for x in labels]
  data = [go.Bar(x=[x for x,y in label_with_value_list], y=labels)]
  plot_data(data, **kwargs)

def plot_dict_as_bar(d, **kwargs):
  data = []
  items = list(d.items())
  items.sort(key=lambda x: x[1], reverse=True)
  plot_bar(items, **kwargs)

def plot_dict_as_bar_percent(d, **kwargs):
  data = []
  nd = {}
  val_sum = sum(d.values())
  for k,v in d.items():
    nd[k] = v / val_sum
  items = list(nd.items())
  items.sort(key=lambda x: x[1], reverse=True)
  plot_bar(items, **kwargs)

def plot_heatmap(heatmap_data, **kwargs):
  ticktext = kwargs.get('ticktext')
  colorscale = kwargs.get('colorscale')
  
  heatmap = go.Heatmap(z = heatmap_data)
  heatmap.colorscale = 'Viridis' # Greys
  if colorscale is not None:
    heatmap.colorscale = colorscale
  heatmap.showscale = True
  if ticktext is not None:
    heatmap.colorbar = dict(
      tickmode = 'array',
      tickvals = list(range(len(ticktext))),
      ticktext = ticktext,
    )
  data = [ heatmap ]
  plot_data(data, **kwargs)

def plot_dictdict_as_bar(d_dict, **kwargs):
  data = []
  for label,d in d_dict.items():
    items = list(d.items())
    items.sort(key=lambda x: x[1], reverse=True)
    data.append(go.Bar(x=[x for x,y in items], y=[y for x,y in items], name=label))
  plot_data(data, **kwargs)



#print(go.Heatmap.colorbar)
#print(go.nticks)



# plot_heatmap(
#   [[3,5],[6,7]],
#   ticktext=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'],
#   title='Plot title',
#   xlabel='x label',
#   ylabel='y label',
# )



# plot_dictdict_as_bar({'first': {'a': 3, 'b': 5}, 'second': {'a': 4, 'b': 6}})





