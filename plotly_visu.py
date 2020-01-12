import plotly.offline as go_offline
import plotly.graph_objects as go

def plotly_draw_landscape(xi, yi, zi, n_points):
    fig=go.Figure()
    #TODO change colorscale to custom
    colorscale = [
        [0.0, "rgb(77, 38, 0)"],
        [0.1, "rgb(153, 102, 51)"],
        [0.3, "rgb(134, 179, 0)"],
        [0.6, "rgb(51, 153, 51)"],
        [1.0, "rgb(204, 255, 255)"]]
    #camera
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=0.0, y=-2.5, z=0.7))
    fig.add_trace(go.Surface(x=xi, y=yi, z=zi, colorscale=colorscale, showscale=False))
    fig.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=1)),
                      scene_camera=camera)
    go_offline.plot(fig, filename='mod1.html',validate=True, auto_open=True)