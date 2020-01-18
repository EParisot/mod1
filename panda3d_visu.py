from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
                         GeomVertexData, GeomVertexWriter, \
                         GeomVertexRewriter, GeomVertexReader, \
                         GeomTriangles, \
                         DirectionalLight, AmbientLight, \
                         TransparencyAttrib, PerlinNoise2
import numpy as np

class Events_Handler(DirectObject.DirectObject):
    def __init__(self, base):
        self.base = base
        self.run = True
        self.accept("space", self.handle_flood)

    def handle_flood(self):
        if self.run == True:
            self.base.taskMgr.remove("flood")
        else:
            self.base.taskMgr.add(self.base.flood, "flood")
        self.run = not self.run

class MyApp(ShowBase):

    def __init__(self, landscape, n_points):
        self.x = landscape[0]
        self.y = landscape[1]
        self.lz = landscape[2]
        self.wz = np.ones((n_points, n_points))
        self.n_points = n_points

        ShowBase.__init__(self)
        self.setBackgroundColor(0,0,0)
        self.trackball.node().setPos(0, 250, -50)

        self.landscape_nodePath = self.draw_landscape_mesh()
        self.landscape_nodePath.setPos(-50, -50, 0)
        self.water_nodePath, self.water_border_nodePath = self.draw_water_mesh()
        self.water_nodePath.setPos(-50, -50, 0)
        self.water_border_nodePath.setPos(-50, -50, 0)
        self.create_light()

        self.noise = PerlinNoise2()
        self.noise.setScale(16)

        ev = Events_Handler(self)
        

    def create_light(self):
        # Directional light 01
        directionalLight = DirectionalLight('directionalLight')
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing backwards, towards the camera.
        directionalLightNP.setHpr(150, -50, 0)
        render.setLight(directionalLightNP)
        # Directional light 02
        directionalLight = DirectionalLight('directionalLight')
        directionalLightNP = render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(50, -80, 0)
        render.setLight(directionalLightNP)

        
    def draw_landscape_mesh(self):
        _format = GeomVertexFormat.get_v3n3cp()
        vdata = GeomVertexData('terrain', _format, Geom.UHStatic)
        vdata.setNumRows(self.n_points**2)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for j in range(self.n_points):
            for i in range(self.n_points):
                vertex.addData3f(self.x[j][i], self.y[j][i], self.lz[j][i])
                if self.lz[j][i] < 2:
                    color.addData4f(0.3, 0.2, 0.1, 1)
                elif self.lz[j][i] < 5:
                    color.addData4f(0.8, 0.8, 0.4, 1)
                elif self.lz[j][i] < 50:
                    color.addData4f(0, 0.5, 0, 1)
                elif self.lz[j][i] < 70:
                    color.addData4f(0, 0.3, 0, 1)
                elif self.lz[j][i] < 80:
                    color.addData4f(0.7, 0.7, 0.7, 1)
                else:
                    color.addData4(0.8, 1, 1, 1)

                n = np.array([self.x[j][i], self.y[j][i], self.lz[j][i]])
                norm = n / np.linalg.norm(n)
                normal.addData3f(norm[0], norm[1], norm[2])

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
        prim.closePrimitive()
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        landscape_nodePath = render.attachNewNode(node)
        return landscape_nodePath

    def draw_water_mesh(self):
        _format = GeomVertexFormat.get_v3n3cp()
        vdata = GeomVertexData('water', _format, Geom.UHDynamic)
        vdata.setNumRows(self.n_points**2)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        for j in range(self.n_points):
            for i in range(self.n_points):
                vertex.addData3f(self.x[j][i], self.y[j][i], self.wz[j][i])
                color.addData4f(0.3, 0.3, 1, 0.8)
                n = np.array([self.x[j][i], self.y[j][i], self.wz[j][i]])
                norm = n / np.linalg.norm(n)
                normal.addData3f(norm[0], norm[1], norm[2])
        prim = GeomTriangles(Geom.UHDynamic)
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
        prim.closePrimitive()
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        water_nodePath = render.attachNewNode(node)
        water_nodePath.setTransparency(TransparencyAttrib.MAlpha)

        # Border
        vdata = GeomVertexData('water_border', _format, Geom.UHDynamic)
        vdata.setNumRows(8)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        for i in [0, 99]:
            vertex.addData3f(i, 0, 1)
            color.addData4f(0.3, 0.3, 1, 0.8)
            vertex.addData3f(i, 0, 0)
            color.addData4f(0.3, 0.3, 1, 0.8)
        for i in [99, 0]:
            vertex.addData3f(i, 99, 1)
            color.addData4f(0.3, 0.3, 1, 0.8)
            vertex.addData3f(i, 99, 0)
            color.addData4f(0.3, 0.3, 1, 0.8)
        prim = GeomTriangles(Geom.UHDynamic)
        for i in range(0, 8, 2):
            prim.add_vertices(i, i+1 if i+1 < 8 else i+1-8, i+2 if i+2 < 8 else i+2-8)
            prim.add_vertices(i+2 if i+2 < 8 else i+2-8, i+1 if i+1 < 8 else i+1-8, i+3 if i+3 < 8 else i+3-8)
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        water_border_nodePath = render.attachNewNode(node)
        water_border_nodePath.setTransparency(TransparencyAttrib.MAlpha)

        return water_nodePath, water_border_nodePath

    def flood(self, task):
        if task.time + 1 < self.n_points:
            water_node = self.water_nodePath.node()
            water_geom = water_node.modifyGeom(0)
            water_data = water_geom.modifyVertexData()
            water_data.setNumRows(self.n_points**2)
            vertex = GeomVertexRewriter(water_data, 'vertex')
            normal = GeomVertexRewriter(water_data, 'normal')
            for j in range(self.n_points):
                for i in range(self.n_points):
                    # Noise
                    offset = task.time * 12
                    waves = self.noise.noise(i + offset, j + offset) * np.random.uniform(0.6, 1) * 10 * task.time / 100
                    # flood
                    self.wz[j][i] = task.time + 1 + (waves \
                        if j != 0 and i != 0 and j != self.n_points-1 and i != self.n_points-1 else 0) # borders
                    v = vertex.getData3f()
                    vertex.setData3f(v[0], v[1], self.wz[j][i])
                    n = np.array([v[0], v[1], self.wz[j][i]])
                    norm = n / np.linalg.norm(n)
                    normal.setData3f(norm[0], norm[1], norm[2])

            water_border_node = self.water_border_nodePath.node()
            water_border_geom = water_border_node.modifyGeom(0)
            water_border_data = water_border_geom.modifyVertexData()
            water_border_data.setNumRows(8)
            vertex = GeomVertexRewriter(water_border_data, 'vertex')
            normal = GeomVertexRewriter(water_border_data, 'normal')
            for i in range(0, 8, 2):
                v = vertex.getData3f()
                vertex.setData3f(v[0], v[1], self.wz[j][i])
                n = np.array([v[0], v[1], self.wz[j][i]])
                norm = n / np.linalg.norm(n)
                normal.setData3f(norm[0], norm[1], norm[2])
                v = vertex.getData3f()
                vertex.setData3f(v[0], v[1], 0)
                n = np.array([v[0], v[1], 1e-12])
                norm = n / np.linalg.norm(n)
                normal.setData3f(norm[0], norm[1], norm[2])
            
        else:
            task.done()
        return task.cont
            
    
def panda3d_draw_landscape(landscape, n_points):
    app = MyApp(landscape, n_points)
    app.run()