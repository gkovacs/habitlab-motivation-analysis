#!/usr/bin/env python
# md5: 08b7127550ed2b7719bc411eb8a0e3bb
#!/usr/bin/env python
# coding: utf-8



import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)



def plot_data(data, **kwargs):
  title = kwargs.get('title')
  xlabel = kwargs.get('xlabel')
  ylabel = kwargs.get('ylabel')
  font = kwargs.get('font')
  tozero = kwargs.get('tozero')
  
  layout = go.Layout()
  if title is not None:
    layout.title = go.layout.Title(text = title)
  if xlabel is not None:
    layout.xaxis = go.layout.XAxis(title = xlabel)
  if ylabel is not None:
    layout.yaxis = go.layout.YAxis(title = ylabel)
  if font is not None:
    layout.font = font
  if tozero is not None:
    layout.yaxis.rangemode = 'tozero'
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
  labels = [x for x,y in label_with_value_list]
  remap_labels = kwargs.get('remap_labels')
  orientation = kwargs.get('orientation', 'v')
  if remap_labels is not None:
    labels = [remap_labels.get(x, x) for x in labels]
  if orientation == 'h':
    data = [go.Bar(y=labels, x=[y for x,y in label_with_value_list], orientation=orientation)]
  else:
    data = [go.Bar(x=labels, y=[y for x,y in label_with_value_list], orientation=orientation)]
  plot_data(data, **kwargs)

def plot_dict_as_bar(d, **kwargs):
  data = []
  if kwargs.get('key_order'):
    items = [(x, d[x]) for x in kwargs.get('key_order')]
  else:
    items = list(d.items())
    items.sort(key=lambda x: x[1], reverse=True)
  plot_bar(items, **kwargs)

def plot_dict_as_bar_percent(d, **kwargs):
  nd = {}
  val_sum = sum(d.values())
  for k,v in d.items():
    nd[k] = 100 * v / val_sum
  plot_dict_as_bar(nd, **kwargs)

def plot_dict_as_bar_fraction(d, **kwargs):
  nd = {}
  val_sum = sum(d.values())
  for k,v in d.items():
    nd[k] = v / val_sum
  plot_dict_as_bar(nd, **kwargs)

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
      #tick0 = 0,
      #dtick = 1,
      #autotick = False,
    )
  data = [ heatmap ]
  plot_data(data, **kwargs)

def plot_dictdict_as_bar(d_dict, **kwargs):
  data = []
  remap_labels = kwargs.get('remap_labels', {})
  print(remap_labels)
  for label,d in d_dict.items():
    label = remap_labels.get(label, label)
    print(label)
    items = list(d.items())
    items.sort(key=lambda x: x[1], reverse=True)
    data.append(go.Bar(x=[remap_labels.get(x, x) for x,y in items], y=[y for x,y in items], name=label))
  plot_data(data, **kwargs)





#print(go.Heatmap.colorbar)
#print(go.nticks)



# plot_heatmap(
#   [[0,1],[1,1]],
#   ticktext=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'],
#   title='Plot title',
#   xlabel='x label',
#   ylabel='y label',
#   #colorscale = 'Greys',
#   colorscale = [
#     [0.0, 'rgb(0, 0, 0)'],
#     [0.5, 'rgb(0, 0, 0)'],
#     [0.5, 'rgb(255, 255, 255)'],
#     [1.0, 'rgb(255, 255, 255)'],
#   ],
# )



# plot_heatmap(
#   [[3,5],[6,7]],
#   ticktext=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'],
#   title='Plot title',
#   xlabel='x label',
#   ylabel='y label',
#   colorscale= [
#         [0, 'rgb(0, 0, 0)'],
#         [0.1, 'rgb(0, 0, 0)'],
#         [0.1, 'rgb(20, 20, 20)'],
#         [0.2, 'rgb(20, 20, 20)'],
#         [0.2, 'rgb(40, 40, 40)'],
#         [0.3, 'rgb(40, 40, 40)'],
#         [0.3, 'rgb(60, 60, 60)'],
#         [0.4, 'rgb(60, 60, 60)'],
#         [0.4, 'rgb(80, 80, 80)'],
#         [0.5, 'rgb(80, 80, 80)'],
#         [0.5, 'rgb(100, 100, 100)'],
#         [0.6, 'rgb(100, 100, 100)'],
#         [0.6, 'rgb(120, 120, 120)'],
#         [0.7, 'rgb(120, 120, 120)'],
#         [0.7, 'rgb(140, 140, 140)'],
#         [0.8, 'rgb(140, 140, 140)'],
#         [0.8, 'rgb(160, 160, 160)'],
#         [0.9, 'rgb(160, 160, 160)'],
#         [0.9, 'rgb(180, 180, 180)'],
#         [1.0, 'rgb(180, 180, 180)'],
#     ],
# )



# plot_dictdict_as_bar({'first': {'a': 3, 'b': 5}, 'second': {'a': 4, 'b': 6}})





