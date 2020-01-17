from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
                         GeomVertexData, GeomVertexWriter, \
                         GeomTriangles, \
                         DirectionalLight, AmbientLight
import numpy as np

class MyApp(ShowBase):

    def __init__(self, landscape, n_points):
        self.x = landscape[0]
        self.y = landscape[1]
        self.z = landscape[2]
        self.n_points = n_points

        ShowBase.__init__(self)

        self.draw_mesh()
        self.create_light()


    def create_light(self):
        # Create Ambient Light
        ambientLight = AmbientLight('ambientLight')
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)

        # Directional light 01
        directionalLight = DirectionalLight('directionalLight')
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing backwards, towards the camera.
        directionalLightNP.setHpr(180, -20, 0)
        render.setLight(directionalLightNP)

        # Directional light 02
        directionalLight = DirectionalLight('directionalLight')
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing forwards, away from the camera.
        directionalLightNP.setHpr(0, -20, 0)
        render.setLight(directionalLightNP)
        
    def draw_mesh(self):
        _format = GeomVertexFormat.get_v3n3cp()
        vdata = GeomVertexData('terrain', _format, Geom.UHStatic)
        vdata.setNumRows(self.n_points**2)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for j in range(self.n_points):
            for i in range(self.n_points):
                vertex.addData3f(self.x[j][i], self.y[j][i], self.z[j][i])
                if self.z[j][i] < 2:
                    color.addData4(0.3, 0.2, 0.1, 1)
                elif self.z[j][i] < 5:
                    color.addData4(0.8, 0.8, 0.4, 1)
                elif self.z[j][i] < 50:
                    color.addData4f(0, 0.5, 0, 1)
                elif self.z[j][i] < 70:
                    color.addData4f(0, 0.3, 0, 1)
                elif self.z[j][i] < 80:
                    color.addData4(0.7, 0.7, 0.7, 1)
                else:
                    color.addData4(0.8, 1, 1, 1)

                if j != self.n_points-1 and i != self.n_points-1:
                    a = np.array([self.x[j][i], self.y[j][i], self.z[j][i]])
                    b = np.array([self.x[j][i+1], self.y[j][i+1], self.z[j][i+1]])
                    c = np.array([self.x[j+1][i], self.y[j+1][i], self.z[j+1][i]])
                    n = np.cross(b - a, c - a)
                    norm = n / np.linalg.norm(n)
                    normal.addData3f(norm[0], norm[1], norm[2])
                else:
                    normal.addData3f(0, 0, 1)
        
        prim = GeomTriangles(Geom.UHStatic)
        for j in range(self.n_points):
            for i in range(self.n_points):
                if j != self.n_points-1 and i != self.n_points-1:
                    prim.add_vertices(j*(self.n_points) + i,
                                      j*(self.n_points) + (i+1),
                                      (j+1)*(self.n_points) + i)
                    prim.add_vertices(j*(self.n_points) + (i+1),
                                      (j+1)*(self.n_points) + (i+1),
                                      (j+1)*(self.n_points) + i)

        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        nodePath = render.attachNewNode(node)
        
def panda3d_draw_landscape(landscape, n_points):
    app = MyApp(landscape, n_points)
    app.run()