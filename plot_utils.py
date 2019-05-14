#!/usr/bin/env python
# md5: 36b13cfd7c8184ac9beee4052e2af6ab
#!/usr/bin/env python
# coding: utf-8



import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)



def plot_histogram(x_values):
  data = [go.Histogram(x=x_values)]
  iplot(data)

def plot_points(points):
  data = [go.Scatter(x=[x for x,y in points], y=[y for x,y in points])]
  iplot(data)

def plot_several_points(points_list):
  data = []
  for label,points in points_list:
    data.append(go.Scatter(x=[x for x,y in points], y=[y for x,y in points], name=label))
  iplot(data)

def plot_bar(label_with_value_list):
  data = [go.Bar(x=[x for x,y in label_with_value_list], y=[y for x,y in label_with_value_list])]
  iplot(data)

def plot_dict_as_bar(d):
  data = []
  items = list(d.items())
  items.sort(key=lambda x: x[1], reverse=True)
  plot_bar(items)

def plot_heatmap(heatmap_data):
  data = [go.Heatmap(z=heatmap_data)]
  iplot(data)









