# tetrahedral_demo_geomkeys.py
# -------------------------------------------------------------------------
# Rotations are attached to geometric triangles, not to vertex labels.
# Key 1 -> outer (convex-hull) triangle
# Keys 2,3,4 -> the three inner triangles in clockwise order around the hull
# -------------------------------------------------------------------------
import pygame, sys, math, numpy as np

# ----- tetrahedron in 3-D ---------------------------------------------------
h = math.sqrt(2/3)
verts = np.array([
    [0.0,                    0.0,  h],          # 0  (was A)
    [1/math.sqrt(3),         0.0,  0.0],        # 1  (was B)
    [-1/(2*math.sqrt(3)),    0.5,  0.0],        # 2  (was C)
    [-1/(2*math.sqrt(3)),   -0.5,  0.0]         # 3  (was D)
])
labels = ["A","B","C","D"]
centre = verts.mean(axis=0)

# ---------- pygame boiler-plate --------------------------------------------
pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Tetrahedral group – geometric key-mapping")
font   = pygame.font.SysFont(None, 24)
clock  = pygame.time.Clock()

SCALE, OFFSET = 200, np.array([400,300])
edges   = [(i,j) for i in range(4) for j in range(i+1,4)]

def project(v):               # orthographic: drop z, then scale + shift
    return (v[:,:2]*SCALE + OFFSET).astype(int)

# ---------- geometry helpers -----------------------------------------------
def inside_triangle(p, a, b, c):
    """True iff p lies strictly inside △ABC (2-D points)."""
    # barycentric coordinates test
    v0, v1, v2 = b-a, c-a, p-a
    dot00, dot01, dot02 = np.dot(v0,v0), np.dot(v0,v1), np.dot(v0,v2)
    dot11, dot12 = np.dot(v1,v1), np.dot(v1,v2)
    denom = dot00*dot11 - dot01*dot01
    if denom == 0:         # degenerate (should never happen for tetrahedron)
        return False
    u = (dot11*dot02 - dot01*dot12) / denom
    v = (dot00*dot12 - dot01*dot02) / denom
    return (u > 0) and (v > 0) and (u+v < 1)

def current_faces():
    """Return dict keyed by pygame.K_1 … K_4:
       value = (face_vertices(tuple idx), axis_idx, name)"""
    P = project(verts)
    # --- find interior (apex) point: the one inside triangle of the others
    apex = None
    for i in range(4):
        others = [j for j in range(4) if j != i]
        if inside_triangle(P[i], P[others[0]], P[others[1]], P[others[2]]):
            apex = i
            break
    if apex is None:                       # numerical fallback: max z
        apex = int(np.argmax(verts[:,2]))
    outer = [j for j in range(4) if j != apex]
    # order outer vertices clockwise around their 2-D centroid
    c2d = P[outer].mean(axis=0)
    ang = [math.atan2(*(p-c2d)[::-1]) for p in P[outer]]  # y,x order
    outer = [v for _,v in sorted(zip(ang, outer))]        # clockwise
    o0,o1,o2 = outer
    # faces and their opposite (rotation-axis) vertex
    faces = {
        pygame.K_1: ((o0,o1,o2), apex, "outer"),
        pygame.K_2: ((apex,o0,o1), o2, "inner-1"),
        pygame.K_3: ((apex,o1,o2), o0, "inner-2"),
        pygame.K_4: ((apex,o2,o0), o1, "inner-3"),
    }
    return faces

def R_matrix(axis, theta):
    """Rodrigues rotation matrix."""
    axis = axis/np.linalg.norm(axis)
    a = math.cos(theta/2.0)
    b,c,d = -axis*math.sin(theta/2.0)
    aa,bb,cc,dd = a*a, b*b, c*c, d*d
    bc,ad,ac,ab,bd,cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([
       [aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
       [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
       [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]
    ])

# ---------- animation state -------------------------------------------------
steps_left = 0
R_step     = None
face_highlight = None
fps_anim   = 45
total_steps = 30
angle_total = -2*math.pi/3        # –120° (CW)

# ---------- main loop -------------------------------------------------------
running = True
while running:
    faces_now = current_faces()          # recomputed every frame

    for ev in pygame.event.get():
        if   ev.type == pygame.QUIT: running = False
        elif (ev.type == pygame.KEYDOWN and
              ev.key in faces_now and steps_left==0):
            face_highlight, axis_idx, _ = faces_now[ev.key]
            axis_vec   = verts[axis_idx] - centre
            R_step     = R_matrix(axis_vec, angle_total/total_steps)
            steps_left = total_steps

    if steps_left:
        verts[:] = (verts - centre) @ R_step.T + centre
        steps_left -= 1
        if steps_left == 0: face_highlight = None

    # ---------- drawing -----------------------------------------------------
    screen.fill((250,250,250))
    Q = project(verts)
    for i,j in edges:
        col  = (30,30,30)
        width = 2
        if face_highlight and i in face_highlight and j in face_highlight:
            col, width = (30,180,30), 4
        pygame.draw.line(screen, col, Q[i], Q[j], width)

    for idx,p in enumerate(Q):
        pygame.draw.circle(screen, (200,30,30), p, 6)
        screen.blit(font.render(labels[idx], True, (20,20,20)),
                    (p[0]+8, p[1]-8))

    screen.blit(font.render("Keys: 1=outer, 2-4 = inner triangles (CW order)",
                             True, (0,0,100)), (10,10))
    pygame.display.flip()
    clock.tick(fps_anim)

pygame.quit()
sys.exit()
