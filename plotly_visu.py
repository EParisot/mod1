import plotly.offline as go_offline
import plotly.graph_objects as go

def plotly_draw_landscape(xi, yi, zi, n_points):
    colorscale = [
        [0.0, "rgb(77, 38, 0)"],
        [0.1, "rgb(153, 102, 51)"],
        [0.3, "rgb(134, 179, 0)"],
        [0.6, "rgb(51, 153, 51)"],
        [1.0, "rgb(204, 255, 255)"]]

    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=0.0, y=-2.5, z=0.7))
    
    fig=go.Figure(
        data=go.Surface(x=xi, y=yi, z=zi, colorscale=colorscale, showscale=False),
        layout=go.Layout(scene=dict(aspectratio=dict(x=1, y=1, z=1)),
                         scene_camera=camera,
                         updatemenus=[dict(type="buttons",
                                       buttons=[dict(label="Play",
                                                     method="animate",
                                                     args=[None])])]),
        frames=[go.Frame(data=[go.Surface(x=xi, y=yi, z=zi+k, colorscale=colorscale, showscale=False)]) for k in range(42)]
    )
    fig.show()
