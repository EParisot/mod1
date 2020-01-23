from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, Geom, GeomTriangles, GeomPoints, \
                         GeomNode, GeomVertexFormat, GeomVertexData, \
                         GeomVertexWriter, GeomVertexRewriter, GeomVertexReader, \
                         DirectionalLight, TransparencyAttrib, AntialiasAttrib
import numpy as np
from event_handler import Events_Handler

loadPrcFileData("", "window-title Mod1")
loadPrcFileData("", "fullscreen 0") # Set to 1 for fullscreen
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "show-frame-rate-meter #t")
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 2")

class MyApp(ShowBase):
    def __init__(self, landscape, n_points):
        self.x = landscape[0]
        self.y = landscape[1]
        self.lz = landscape[2]
        self.wz = np.ones((n_points, n_points))
        self.rz = np.zeros((n_points, n_points)) + n_points
        self.n_points = n_points
        self.details = 4
        self.H = 1                                                          # Depth of fluid [m] at start
        self.g = 9.81                                                       # Acceleration of gravity [m/s^2]
        self.N_x = self.n_points // self.details                            # Number of grid points in x-direction
        self.N_y = self.n_points // self.details                            # Number of grid points in y-direction
        self.dx = self.n_points/(self.N_x - 1)                              # Grid spacing in x-direction
        self.dy = self.n_points/(self.N_y - 1)                              # Grid spacing in y-direction
        self.dt = 0.1*min(self.dx, self.dy)/np.sqrt(self.g * self.H)        # Time step (defined from the CFL condition)
        self.u_n = np.zeros((self.N_x, self.N_y))                           # To hold u at current time step
        self.v_n = np.zeros((self.N_x, self.N_y))                           # To hold v at current time step

        # Initial conditions for u and v.
        self.u_n[:, :] = 0.0                                                # Initial condition for u
        self.v_n[:, :] = 0.0                                                # Initial condition for u
        self.u_n[-1, :] = 0.0                                               # Ensuring initial u satisfy BC
        self.v_n[:, -1] = 0.0                                               # Ensuring initial v satisfy BC

        # Init Window
        ShowBase.__init__(self)
        self.setBackgroundColor(0,0,0)
        self.trackball.node().setPos(0, 250, -50)

        # Init Meshes
        self.landscape_nodePath = self.draw_landscape_mesh()
        self.draw_water_mesh()
        self.draw_rain_mesh()
        self.create_light()

        self.raining = False
        self.flush = False
        self.flooding = False

        # Wait for events
        Events_Handler(self)
        
    def create_light(self):
        directionalLight = DirectionalLight('directionalLight1')
        directionalLightNP = render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(150, -50, 0)
        render.setLight(directionalLightNP)
        directionalLight = DirectionalLight('directionalLight2')
        directionalLightNP = render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(50, -80, 0)
        render.setLight(directionalLightNP)

    def draw_landscape_mesh(self):
        _format = GeomVertexFormat.get_v3n3cp()
        self.landscape_vdata = GeomVertexData('terrain', _format, Geom.UHStatic)
        self.landscape_vdata.setNumRows(self.n_points**2)
        vertex = GeomVertexWriter(self.landscape_vdata, 'vertex')
        normal = GeomVertexWriter(self.landscape_vdata, 'normal')
        color = GeomVertexWriter(self.landscape_vdata, 'color')
        for j in range(self.n_points):
            for i in range(self.n_points):
                # Terrain Vertices
                vertex.addData3f(self.x[j][i], self.y[j][i], self.lz[j][i])
                # Terrain Colors
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
                    color.addData4f(0.8, 1, 1, 1)
                # Terrain Normals
                if self.lz[j][i] != 0:
                    n = np.array([self.x[j][i], self.y[j][i], self.lz[j][i]])
                else:
                    n = np.array([self.x[j][i], self.y[j][i], 1e-12])
                norm = n / np.linalg.norm(n)
                normal.addData3f(norm[0], norm[1], norm[2])
        # Terrain Primitive
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
        geom = Geom(self.landscape_vdata)
        prim.closePrimitive()
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        landscape_nodePath = render.attachNewNode(node)
        landscape_nodePath.setPos(-50, -50, 0)
        landscape_nodePath.setAntialias(AntialiasAttrib.MAuto)
        return landscape_nodePath

    def draw_water_mesh(self):
        _format = GeomVertexFormat.get_v3n3cp()
        self.water_vdata = GeomVertexData('water', _format, Geom.UHDynamic)
        self.water_vdata.setNumRows((self.n_points // self.details)**2)
        vertex = GeomVertexWriter(self.water_vdata, 'vertex')
        normal = GeomVertexWriter(self.water_vdata, 'normal')
        color = GeomVertexWriter(self.water_vdata, 'color')
        
        for j in range(0, self.n_points, self.details):
            for i in range(0, self.n_points, self.details):
                if j == self.n_points - self.details:
                    j = self.n_points - 1
                if i == self.n_points - self.details:
                    i = self.n_points - 1
                # Water Vertices
                vertex.addData3f(self.x[j][i], self.y[j][i], self.wz[j][i])
                # Water Color
                color.addData4f(0.3, 0.3, 1, 0.8)
                # water Normals
                n = np.array([self.x[j][i], self.y[j][i], self.wz[j][i]])
                norm = n / np.linalg.norm(n)
                normal.addData3f(norm[0], norm[1], norm[2])
        # Water Primitive
        prim = GeomTriangles(Geom.UHDynamic)
        for j in range(self.n_points//self.details):
            for i in range(self.n_points//self.details):
                if j != (self.n_points//self.details)-1 and i != (self.n_points//self.details)-1:
                    prim.add_vertices(j*(self.n_points//self.details) + i,
                                    j*(self.n_points//self.details) + (i+1),
                                    (j+1)*(self.n_points//self.details) + i)
                    prim.add_vertices(j*(self.n_points//self.details) + (i+1),
                                    (j+1)*(self.n_points//self.details) + (i+1),
                                    (j+1)*(self.n_points//self.details) + i)
        geom = Geom(self.water_vdata)
        prim.closePrimitive()
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        water_nodePath = render.attachNewNode(node)
        water_nodePath.setTransparency(TransparencyAttrib.MAlpha)
        water_nodePath.setAntialias(AntialiasAttrib.MAuto)
        water_nodePath.setPos(-50, -50, 0)

        # Border
        self.water_border_vdata = GeomVertexData('water_border', _format, Geom.UHDynamic)
        self.water_border_vdata.setNumRows(8)
        vertex = GeomVertexWriter(self.water_border_vdata, 'vertex')
        normal = GeomVertexRewriter(self.water_border_vdata, 'normal')
        color = GeomVertexWriter(self.water_border_vdata, 'color')
        for i in [0, 99]:
            for j in range(1, -1, -1):
                # Borders Vertices
                vertex.addData3f(i, 0, j)
                # Borders Colors
                color.addData4f(0.3, 0.3, 1, 0.8)
                # Borders Normals
                n = np.array([i, 0, 1e-12 if j == 0 else 1])
                norm = n / np.linalg.norm(n)
                normal.addData3f(norm[0], norm[1], norm[2])
        for i in [99, 0]:
            for j in range(1, -1, -1):
                vertex.addData3f(i, 99, j)
                color.addData4f(0.3, 0.3, 1, 0.8)
                n = np.array([i, 99, 1e-12 if j == 0 else 1])
                norm = n / np.linalg.norm(n)
                normal.addData3f(norm[0], norm[1], norm[2])
        # Borders Primitive
        prim = GeomTriangles(Geom.UHDynamic)
        for i in range(0, 8, 2):
            prim.add_vertices(i, i+1 if i+1 < 8 else i+1-8, \
                i+2 if i+2 < 8 else i+2-8)
            prim.add_vertices(i+2 if i+2 < 8 else i+2-8, \
                i+1 if i+1 < 8 else i+1-8, i+3 if i+3 < 8 else i+3-8)
        geom = Geom(self.water_border_vdata)
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        water_border_nodePath = render.attachNewNode(node)
        water_border_nodePath.setTransparency(TransparencyAttrib.MAlpha)
        water_border_nodePath.setAntialias(AntialiasAttrib.MAuto)
        water_border_nodePath.setPos(-50, -50, 0)

    def draw_rain_mesh(self):
        _format = GeomVertexFormat.get_v3cp()
        self.rain_vdata = GeomVertexData('rain', _format, Geom.UHDynamic)
        self.rain_vdata.setNumRows(self.n_points**2)
        vertex = GeomVertexWriter(self.rain_vdata, 'vertex')
        color = GeomVertexWriter(self.rain_vdata, 'color')
        for j in range(self.n_points):
            for i in range(self.n_points):
                # Rain Vertices
                vertex.addData3f(self.x[j][i], self.y[j][i], self.n_points)
                # Rain Colors
                color.addData4f(0.3, 0.3, 1, 0)
        # Rain Primitive
        prim = GeomPoints(Geom.UHDynamic)
        for j in range(self.n_points):
            for i in range(self.n_points):
                    prim.add_vertices(j*(self.n_points) + i,
                                      j*(self.n_points) + i,
                                      j*(self.n_points) + i)
        geom = Geom(self.rain_vdata)
        prim.closePrimitive()
        geom.addPrimitive(prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        rain_nodePath = render.attachNewNode(node)
        rain_nodePath.setTransparency(TransparencyAttrib.MAlpha)
        rain_nodePath.setAntialias(AntialiasAttrib.MAuto)
        rain_nodePath.setRenderModeThickness(2)
        rain_nodePath.setPos(-50, -50, 0)

    def handle_last_puddles(self):
        for j in range(0, self.n_points, self.details):
            for i in range(0, self.n_points, self.details):
                if self.wz[j][i] > self.H and \
                            self.wz[j][i] > self.lz[j][i] and \
                            self.wz[j][i] - self.lz[j][i] < 10:
                    self.wz[j][i] -= self.dt

    def flood(self, task=None):
        # Animate Water Surface
        step_np1 = self.water_physic()
        vertex = GeomVertexRewriter(self.water_vdata, 'vertex')
        normal = GeomVertexRewriter(self.water_vdata, 'normal')
        for j in range(0, self.n_points, self.details):
            for i in range(0, self.n_points, self.details):
                # Flood
                if j != 0 and i != 0 and j != self.n_points - self.details and \
                                        i != self.n_points - self.details:
                    self.wz[j][i] = step_np1[j//self.details][i//self.details]
                else:
                    self.wz[j][i] = self.H # borders condition
                v = vertex.getData3f()
                vertex.setData3f(v[0], v[1], self.wz[j][i])
                n = np.array([v[0], v[1], self.wz[j][i]])
                norm = n / np.linalg.norm(n)
                normal.setData3f(norm[0], norm[1], norm[2])
        # Extend Water Borders
        vertex = GeomVertexRewriter(self.water_border_vdata, 'vertex')
        normal = GeomVertexRewriter(self.water_border_vdata, 'normal')
        for i in range(0, 8, 2):
            v = vertex.getData3f()
            vertex.setData3f(v[0], v[1], self.H)
            n = np.array([v[0], v[1], self.H])
            norm = n / np.linalg.norm(n)
            normal.setData3f(norm[0], norm[1], norm[2])
            v = vertex.getData3f()
            vertex.setData3f(v[0], v[1], 0)
            n = np.array([v[0], v[1], 1e-12])
            norm = n / np.linalg.norm(n)
            normal.setData3f(norm[0], norm[1], norm[2])
        # animate level
        if self.flooding == True and self.flush == False and self.H < self.n_points:
            self.H += self.dt
        elif self.flush == True and self.H > 1:
            self.H -= self.dt
            # handle last puddles
            self.handle_last_puddles()
        if task:
            return task.cont

    def wave(self, task):
        # Compute physic
        step_np1 = self.water_physic()
        self.H += 0.1 * (np.mean(step_np1) - self.H)
        # render wave
        vertex = GeomVertexRewriter(self.water_vdata, 'vertex')
        normal = GeomVertexRewriter(self.water_vdata, 'normal')
        for j in range(0, self.n_points, self.details):
            for i in range(0, self.n_points, self.details):
                self.wz[j][i] = step_np1[j//self.details][i//self.details]
                v = vertex.getData3f()
                if j != 0 and i != 0 and j != self.n_points - self.details and \
                                            i != self.n_points - self.details:
                    vertex.setData3f(v[0], v[1], self.wz[j][i])
                    n = np.array([v[0], v[1], self.wz[j][i]])
                else:
                    vertex.setData3f(v[0], v[1], self.H)
                    n = np.array([v[0], v[1], self.H])
                norm = n / np.linalg.norm(n)
                normal.setData3f(norm[0], norm[1], norm[2])
        # Extend Water Borders
        vertex = GeomVertexRewriter(self.water_border_vdata, 'vertex')
        normal = GeomVertexRewriter(self.water_border_vdata, 'normal')
        for i in range(0, 8, 2):
            v = vertex.getData3f()
            vertex.setData3f(v[0], v[1], self.H)
            n = np.array([v[0], v[1], self.H])
            norm = n / np.linalg.norm(n)
            normal.setData3f(norm[0], norm[1], norm[2])
            v = vertex.getData3f()
            vertex.setData3f(v[0], v[1], 0)
            n = np.array([v[0], v[1], 1e-12])
            norm = n / np.linalg.norm(n)
            normal.setData3f(norm[0], norm[1], norm[2])
        # handle last puddles
        self.handle_last_puddles()
        return task.cont
        
    def rain(self, task):
        # animate level
        self.flood()
        # Animate Rain 
        speed = 1.0
        vertex = GeomVertexRewriter(self.rain_vdata, 'vertex')
        color = GeomVertexWriter(self.rain_vdata, 'color')
        moving = np.random.choice([0, 1], size=(self.n_points, self.n_points),
                                  p=[999/1000, 1./1000])
        moved = 0
        for j in range(self.n_points):
            for i in range(self.n_points):
                # rain
                v = vertex.getData3f()
                # start falling
                if v[2] == self.n_points:
                    if moving[j][i] == 1 and self.raining == True:
                        self.rz[j][i] -= speed
                        vertex.setData3f(v[0], v[1], self.rz[j][i])
                        color.setData4f(0.3, 0.3, 1, 1)
                        moved += 1
                    else:
                        vertex.setData3f(v[0], v[1], v[2])
                        color.setData4f(0.3, 0.3, 1, 0)
                # keep falling
                elif self.rz[j][i] > self.lz[j][i]:
                    if self.rz[j][i]-speed > self.lz[j][i]:
                        self.rz[j][i] -= speed
                    else:
                        self.rz[j][i] = self.lz[j][i]
                    vertex.setData3f(v[0], v[1], self.rz[j][i])
                    if self.rz[j][i] > self.wz[j][i]:
                        color.setData4f(0.3, 0.3, 1, 1)
                    else:
                        color.setData4f(0.3, 0.3, 1, 0)
                    moved += 1
                # stop falling
                else:
                    # handle rolling drops
                    v = list(map(int, v))
                    if v[1]+1 < self.n_points and v[0]+1 < self.n_points and v[1]-1 >= 0 and v[0]-1 >= 0:
                        diff_list = np.array([self.lz[v[1]+1][v[0]], 
                                                self.lz[v[1]][v[0]+1], 
                                                self.lz[v[1]-1][v[0]], 
                                                self.lz[v[1]][v[0]-1]])
                        diff_list = self.lz[v[1]][v[0]] - diff_list
                        max_idx = np.argmax(diff_list)
                        if diff_list[max_idx] > 1e-12:
                            if max_idx == 0:
                                self.rz[j][i] = self.lz[v[1]+1][v[0]]
                                vertex.setData3f(v[0], v[1]+1, self.rz[j][i])
                                if self.rz[j][i] > self.wz[j][i]:
                                    color.setData4f(0.3, 0.3, 1, 1)
                                else:
                                    color.setData4f(0.3, 0.3, 1, 0)
                                moved += 1
                            elif max_idx == 1:
                                self.rz[j][i] = self.lz[v[1]][v[0]+1]
                                vertex.setData3f(v[0]+1, v[1], self.rz[j][i])
                                if self.rz[j][i] > self.wz[j][i]:
                                    color.setData4f(0.3, 0.3, 1, 1)
                                else:
                                    color.setData4f(0.3, 0.3, 1, 0)
                                moved += 1
                            elif max_idx == 2:
                                self.rz[j][i] = self.lz[v[1]-1][v[0]]
                                vertex.setData3f(v[0], v[1]-1, self.rz[j][i])
                                if self.rz[j][i] > self.wz[j][i]:
                                    color.setData4f(0.3, 0.3, 1, 1)
                                else:
                                    color.setData4f(0.3, 0.3, 1, 0)
                                moved += 1
                            elif max_idx == 3:
                                self.rz[j][i] = self.lz[v[1]][v[0]-1]
                                vertex.setData3f(v[0]-1, v[1], self.rz[j][i])
                                if self.rz[j][i] > self.wz[j][i]:
                                    color.setData4f(0.3, 0.3, 1, 1)
                                else:
                                    color.setData4f(0.3, 0.3, 1, 0)
                                moved += 1
                        else:
                            if self.rz[v[1]][v[0]] >= self.wz[v[1]][v[0]]:
                                # handle puddles
                                self.wz[v[1]][v[0]] = self.lz[v[1]][v[0]] + self.H
                                self.wz[v[1]+self.details][v[0]] = self.lz[v[1]][v[0]] + self.H
                                self.wz[v[1]][v[0]+self.details] = self.lz[v[1]][v[0]] + self.H
                                self.wz[v[1]+self.details][v[0]+self.details] = self.lz[v[1]][v[0]] + self.H
                                self.wz[v[1]-self.details][v[0]] = self.lz[v[1]][v[0]] + self.H
                                self.wz[v[1]][v[0]-self.details] = self.lz[v[1]][v[0]] + self.H
                                self.wz[v[1]-self.details][v[0]-self.details] = self.lz[v[1]][v[0]] + self.H
                            color.setData4f(0.3, 0.3, 1, 0)
                            self.rz[j][i] = self.n_points
                            vertex.setData3f(i , j, self.rz[j][i])
                            self.flooding = True
                    else:
                        self.rz[j][i] = self.n_points
                        vertex.setData3f(i , j, self.rz[j][i])
                        color.setData4f(0.3, 0.3, 1, 0)
        if moved == 0:
            self.flooding = False
            return task.done
        return task.cont

    def water_physic(self):
        # recalc dt to avoid explosion as H grows
        self.dt = 0.1*min(self.dx, self.dy)/np.sqrt(self.g * self.H)

        step_n = np.zeros((self.N_x, self.N_y))    # To hold eta at current time step
        step_np1 = np.zeros((self.N_x, self.N_y))  # To hold eta at next time step

        # grab current mesh
        for j in range(0, self.n_points, self.details):
            for i in range(0, self.n_points, self.details):
                step_n[j//self.details][i//self.details] = self.wz[j][i]

        u_np1 = np.zeros((self.N_x, self.N_y))    # To hold u at next time step
        v_np1 = np.zeros((self.N_x, self.N_y))    # To hold v at next time step
        
        # Temporary variables (each time step) for upwind scheme in eta equation
        h_e = np.zeros((self.N_x, self.N_y))
        h_w = np.zeros((self.N_x, self.N_y))
        h_n = np.zeros((self.N_x, self.N_y))
        h_s = np.zeros((self.N_x, self.N_y))
        uhwe = np.zeros((self.N_x, self.N_y))
        vhns = np.zeros((self.N_x, self.N_y))

        # Computing values for u and v at next time step
        u_np1[:-1, :] = self.u_n[:-1, :] - self.g * self.dt/self.dx*(step_n[1:, :] - step_n[:-1, :])
        v_np1[:, :-1] = self.v_n[:, :-1] - self.g * self.dt/self.dy*(step_n[:, 1:] - step_n[:, :-1])
        v_np1[:, -1] = 0.0      # Northern boundary condition
        u_np1[-1, :] = 0.0      # Eastern boundary condition

        # Obstacles boundary condition
        for j in range(0, self.n_points, self.details):
            for i in range(0, self.n_points, self.details):
                if j > 0 and i > 0:
                    if step_n[j//self.details][i//self.details] <= np.max(self.lz[j:j+self.details, i:i+self.details]):
                        if step_n[(j-self.details)//self.details][(i-self.details)//self.details] <= np.max(self.lz[j-self.details:j, i-self.details:i]):
                            v_np1[(j-self.details)//self.details][(i-self.details)//self.details] = 0.0
                            u_np1[(j-self.details)//self.details][(i-self.details)//self.details] = 0.0
                        else:
                            v_np1[j//self.details][i//self.details] = 0.0
                            u_np1[j//self.details][i//self.details] = 0.0

        # Computing arrays needed for the upwind scheme in the eta equation.
        h_e[:-1, :] = np.where(u_np1[:-1, :] > 0, step_n[:-1, :] + self.H, step_n[1:, :] + self.H)
        h_e[-1, :] = step_n[-1, :] + self.H
        
        h_w[1:, :] = np.where(u_np1[:-1, :] > 0, step_n[:-1, :] + self.H, step_n[1:, :] + self.H)
        h_w[0, :] = step_n[0, :] + self.H

        h_n[:, :-1] = np.where(v_np1[:, :-1] > 0, step_n[:, :-1] + self.H, step_n[:, 1:] + self.H)
        h_n[:, -1] = step_n[:, -1] + self.H
        
        h_s[:, 1:] = np.where(v_np1[:, :-1] > 0, step_n[:, :-1] + self.H, step_n[:, 1:] + self.H)
        h_s[:, 0] = step_n[:, 0] + self.H

        uhwe[0, :] = u_np1[0, :]*h_e[0, :]
        uhwe[1:, :] = u_np1[1:, :]*h_e[1:, :] - u_np1[:-1, :]*h_w[1:, :]
        vhns[:, 0] = v_np1[:, 0]*h_n[:, 0]
        vhns[:, 1:] = v_np1[:, 1:]*h_n[:, 1:] - v_np1[:, :-1]*h_s[:, 1:]

        # Computing eta values at next time step
        step_np1[:, :] = step_n[:, :] - self.dt*(uhwe[:, :]/self.dx + vhns[:, :]/self.dy)    # Without source/sink

        self.u_n = np.copy(u_np1)        # Update u for next iteration
        self.v_n = np.copy(v_np1)        # Update v for next iteration

        return step_np1
    
def panda3d_draw_landscape(landscape, n_points):
    app = MyApp(landscape, n_points)
    app.run()
