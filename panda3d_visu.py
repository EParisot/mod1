from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
                         GeomVertexData, GeomVertexWriter, \
                         GeomVertexRewriter, GeomVertexReader, \
                         GeomTriangles, \
                         DirectionalLight, AmbientLight, \
                         TransparencyAttrib

import numpy as np

class MyApp(ShowBase):

    def __init__(self, landscape, n_points):
        self.x = landscape[0]
        self.y = landscape[1]
        self.lz = landscape[2]
        self.wz = np.ones((n_points, n_points))
        self.n_points = n_points

        ShowBase.__init__(self)
        self.setBackgroundColor(0.9,0.9,0.9)
        self.trackball.node().setPos(0, 300, -20)
        self.trackball.node().setHpr(0, 30, 0)

        self.landscape_nodePath = self.draw_landscape_mesh()
        self.landscape_nodePath.setPos(-50, -50, 0)
        self.water_nodePath = self.draw_water_mesh()
        self.water_nodePath.setPos(-50, -50, 0)
        self.create_light()
        self.taskMgr.add(self.animate_water, "water_anim")
        

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
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        water_nodePath = render.attachNewNode(node)
        water_nodePath.setTransparency(TransparencyAttrib.MAlpha)
        return water_nodePath

    def animate_water(self, task):
        if task.time + 1 < self.n_points:

            water_node = self.water_nodePath.node()
            water_geom = water_node.modifyGeom(0)
            water_data = water_geom.modifyVertexData()
            
            water_data.setNumRows(self.n_points**2)
            vertex = GeomVertexRewriter(water_data, 'vertex')
            normal = GeomVertexRewriter(water_data, 'normal')
            for j in range(self.n_points):
                for i in range(self.n_points):
                    v = vertex.getData3f()
                    # flood
                    self.wz[j][i] = task.time + 1
                    # waves computation
                    # TODO

                    # render water
                    vertex.setData3f(v[0], v[1], self.wz[j][i])
                    n = np.array([self.x[j][i], self.y[j][i], self.wz[j][i]])
                    norm = n / np.linalg.norm(n)
                    normal.setData3f(norm[0], norm[1], norm[2])
        else:
            task.done()
        return task.cont
            
    
def panda3d_draw_landscape(landscape, n_points):
    app = MyApp(landscape, n_points)
    app.run()