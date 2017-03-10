from math import *
from time import ctime

# There are twenty side to your average icosahedron. We need
# to select that side which is up. This is done by dotting
# the acceleration vector with the side normals and selecting
# the face number with largest of these.

a = (1.0+sqrt(5.0))/2.0
b = 1.0
c = 0.0
# List of all Icosahedron vertices
vert = (( a, b, c), ( b, c, a), ( c, a, b),
        (-a, b, c), ( b, c,-a), ( c,-a, b),
        ( a,-b, c), (-b, c, a), ( c, a,-b),
        (-a,-b, c), (-b, c,-a), ( c,-a,-b))

# compute dot product of two vertex vectors
def dot(n,m):
    return vert[n][0]*vert[m][0]+vert[n][1]*vert[m][1]+vert[n][2]*vert[m][2]

# define dot product of two 3-vectors
def dotp(a,b):
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

# The angle between two adjacent vertex vectors is always the same
# which implies that the dot product of adjacent vertices will always
# be the same. For our normalization the dot product is just `a`.

# returns a logical bit vector of all verticies connected to the
# n'th vertex.
def connection(n):
    return [True if dot(n,k)==a else False for k in range(12)]

# form the connection matrix. connect[n][m] is True if vert[n] and
# vert[m] are connected by a triangle edge.
connect = [connection(n) for n in range(12)]

# Compute all 20 face vertex lists as tuples of indicies
facelist = set()
for n in range(12):
    for m in range(n):
        for k in range(m):
            if connect[n][m] and connect[n][k] and connect[m][k]:
                facelist.add((n,m,k))

# compute a vector normal to the plane of the two vectors provided
def crossprod(a,b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

# flip the sign of a vector
def negate(a):
    return (-a[0],-a[1],-a[2])

# given a face as a tuple of vertex indicies return a normal vector
def normal(lst):
    a = vert[lst[0]]
    b = vert[lst[1]]
    c = vert[lst[2]]
    x = (b[0]-a[0],b[1]-a[1],b[2]-a[2])
    y = (c[0]-a[0],c[1]-a[1],c[2]-a[2])
    z = crossprod(x,y)
    if (dotp(a,z) < 0.0):
        z = negate(z)
    return z

# form a list of all face normals.
vecs = [normal(p) for p in facelist]

# Here we rotate the set of normals so that we may align the Arduino
# board plane with respect to one (or any) icosahedron faces. We have
# chosen three rotations such that making the y-axis of the Arduino
# parallel to one of the faces of the fave it's mounted to will align
# all normals of the icosahedron with the computed values. (needs testing)
def rotate(r,a):
    return (dotp(r[0],a),dotp(r[1],a),dotp(r[2],a))

r2 = 1.0/sqrt(2.0)
rotz = ((r2,r2,0.0),(-r2,r2,0.0),(0.0,0.0,1.0))

## Makes x a cardinal direction (normal to two faces)
c1 = sqrt(2.0/3.0)
s1 = sqrt(1.0/3.0)
roty = ((c1,0.0,s1),(0.0,1.0,0.0),(-s1,0.0,c1))

## Make board mount on one face with x perp to triangle (face) edge.
## Makes board normal and two face normals colinear.
rot90y = ((0.0,0.0,1.0),(0.0,1.0,0.0),(-1.0,0.0,0.0))

def fixit(v):
    return rotate(rot90y,rotate(roty,rotate(rotz,v)))

intvecs = [tuple([int(x*1000) for x in fixit(v)]) for v in vecs]

def zorder(a,b):
    return b[2] - a[2]

intvecs.sort(zorder)

# output the normal list as a c-structure. Note you should remove
# the last comma if the compiler complains. I instinctually remove
# this last comma after pasting this structure into the Arduino code.
def ppvecs():
    print "//Generated by normals.py on "+ctime()
    print "int normal[20][3] = {"
    for v in intvecs:
        print "   {",v[0],",",v[1],",",v[2],"},"
    print "};"

ppvecs()
