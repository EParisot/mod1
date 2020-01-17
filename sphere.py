from panda3d.core import NodePath, Geom, GeomPoints, GeomNode, \
                         GeomVertexFormat, GeomVertexData, GeomVertexWriter, \
                         GeomVertexRewriter, GeomVertexReader, \
                         GeomTriangles, TransparencyAttrib, Vec3, VBase3
from math import sqrt

def empty(prefix, points = False):
	path = NodePath(prefix + '_path')
	node = GeomNode(prefix + '_node')
	path.attachNewNode(node)

	gvd = GeomVertexData('gvd', GeomVertexFormat.getV3(), Geom.UHStatic)
	geom = Geom(gvd)
	gvw = GeomVertexWriter(gvd, 'vertex')
	node.addGeom(geom)
	if points:
		prim = GeomPoints(Geom.UHStatic)
	else:
		prim = GeomTriangles(Geom.UHStatic)
	return (gvw, prim, geom, path)

def IcoSphere(radius, subdivisions):
	(gvw, prim, geom, path) = empty('ico')

	verts = []
	
	phi = .5*(1.+sqrt(5.))
	invnorm = 1/sqrt(phi*phi+1)

	verts.append(Vec3(-1,  phi, 0) * invnorm)   #0
	verts.append(Vec3( 1,  phi, 0) * invnorm)   #1
	verts.append(Vec3(0,   1,  -phi) * invnorm) #2
	verts.append(Vec3(0,   1,   phi) * invnorm) #3
	verts.append(Vec3(-phi,0,  -1) * invnorm)   #4
	verts.append(Vec3(-phi,0,   1) * invnorm)   #5
	verts.append(Vec3( phi,0,  -1) * invnorm)   #6
	verts.append(Vec3( phi,0,   1) * invnorm)   #7
	verts.append(Vec3(0,   -1, -phi) * invnorm) #8
	verts.append(Vec3(0,   -1,  phi) * invnorm) #9
	verts.append(Vec3(-1,  -phi,0) * invnorm)   #10
	verts.append(Vec3( 1,  -phi,0) * invnorm)   #11

	faces = [
		0,1,2,
		0,3,1,
		0,4,5,
		1,7,6,
		1,6,2,
		1,3,7,
		0,2,4,
		0,5,3,
		2,6,8,
		2,8,4,
		3,5,9,
		3,9,7,
		11,6,7,
		10,5,4,
		10,4,8,
		10,9,5,
		11,8,6,
		11,7,9,
		10,8,11,
		10,11,9
	]

	size = 60

	# Step 2 : tessellate
	for subdivision in range(0,subdivisions):
		size *= 4
		newFaces = []
		for i in range(0, size//12):
			i1 = faces[i*3]
			i2 = faces[i*3+1]
			i3 = faces[i*3+2]
			i12 = len(verts)
			i23 = i12+1
			i13 = i12+2
			v1 = verts[i1]
			v2 = verts[i2]
			v3 = verts[i3]
			# make 1 vertice at the center of each edge and project it onto the sphere
			vt = v1+v2
			vt.normalize()
			verts.append(vt)
			vt = v2+v3
			vt.normalize()
			verts.append(vt)
			vt = v1+v3
			vt.normalize()
			verts.append(vt)
			# now recreate indices
			newFaces.append(i1)
			newFaces.append(i12)
			newFaces.append(i13)
			newFaces.append(i2)
			newFaces.append(i23)
			newFaces.append(i12)
			newFaces.append(i3)
			newFaces.append(i13)
			newFaces.append(i23)
			newFaces.append(i12)
			newFaces.append(i23)
			newFaces.append(i13)
		faces = newFaces
	
	for i in range(0,len(verts)):
		gvw.addData3f(VBase3(verts[i]))
	for i in range(0, len(faces)//3):
		prim.addVertices(faces[i*3],faces[i*3+1],faces[i*3+2])

	prim.closePrimitive()
	geom.addPrimitive(prim)
	
	return path