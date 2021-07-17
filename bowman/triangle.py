from collections import namedtuple
import functools

from sage.all import *

def is_valid_barycentric_coordinate(a0, a1, a2):
    if a0 + a1 + a2 != 1:
        return False
    if a0 < 0 or a1 < 0 or a2 < 0:
        return False
    return True

class Triangle():
    """ A triangle with a list of marked points
    -
    :params v0, v1, v2: vectors representing edges of the triangle with property v0 + v1 + v2 = 0
    :param points_marked: an optional list containing marked points of the form
     ((a, b, c), (r, g, b)) where (a,b,c) are barycentric coords in the triangle and (r, g, b) correspond to a color for the marked point
    -
    - see a document for how the coordinates correspond to the edges
    """
    def __init__(self, v0, v1, v2, points_marked = None):
        if sum((v0, v1, v2)) != 0:
            raise ValueError("sides do not close up")
        elif sage.all.matrix([v0, -v2]).determinant() <= 0:
            raise ValueError("sides are not oriented correctly")

        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

        if points_marked is None:
            self.points_marked = tuple()
        else:
            for point_marked, _ in points_marked:
                if not is_valid_barycentric_coordinate(*(point_marked)):
                    raise ValueError("Invalid barycentric coordinates.")
            self.points_marked = tuple(points_marked)

    def mark_point(self, coords, rgbcolor):
        """Determine if the given coordinates COORDS are valid barycentric coordinates in the Triangle self and add to points_marked if valid.
        return 0 if the cooridnates are valid, 1 otherwise
        """
        if not is_valid_barycentric_coordinate(*coords):
            raise ValueError("Invalid barycentric coordinates.")

        for i in range(len(self.points_marked)):
            point_marked, _ = self.points_marked[i]
            if coords == point_marked:
                # If the point has already been marked, just update the color.
                return Triangle(self.v0, self.v1, self.v2, self.points_marked[0:i] + ((coords, rgbcolor),) + self.points_marked[i+1:])

        # Otherwise, append the point as a new element in self.points_marked.
        return Triangle(self.v0, self.v1, self.v2, self.points_marked + ((coords, rgbcolor),))

    def __getitem__(self, key):
        if key == 0:
            return self.v0
        elif key == 1:
            return self.v1
        elif key == 2:
            return self.v2
        else:
            raise ValueError("Invalid index {i}. A triangle has only three edges.".format(i = key))

    def reflect(self, idx):
        def reflect_vector(v, w):
            w_parallel = (v.dot_product(w) / v.dot_product(v)) * v
            w_perp = w - w_parallel
            return w - 2 * w_perp

        v_axis = self[idx]
        v_succ = self[(idx + 1) % 3]
        v_pred = self[(idx + 2) % 3]
        sides_new = {idx: -v_axis,
                     (idx + 1) % 3: reflect_vector(v_axis, -v_pred),
                     (idx + 2) % 3: reflect_vector(v_axis, -v_succ)}
        return Triangle(sides_new[0], sides_new[1], sides_new[2], self.points_marked)

    def plot(self, basepoint=sage.all.zero_vector(2)):
        triangle_plot = sage.all.polygon2d(self.vertices(basepoint), fill=False).plot()
        for point_marked, point_marked_color in self.points_marked:
            point_marked_coords = basepoint + point_marked[1]*self.v0 - point_marked[2]*self.v2
            triangle_plot = triangle_plot + sage.all.point2d((float(point_marked_coords[0]), float(point_marked_coords[1])), rgbcolor = point_marked_color, size = 50).plot()
        return triangle_plot

    def vertices(self, basepoint=sage.all.zero_vector(2)):
        return [basepoint, basepoint + self.v0, basepoint - self.v2]

    def apply_matrix(self, m):
        w0 = m * self.v0
        w1 = m * self.v1
        w2 = -(w0 + w1)
        return Triangle(w0, w1, w2, self.points_marked)

    def __hash__(self):
        return hash(tuple(coord for vertex in self.vertices() for coord in vertex))

    @property
    def area(self):
        return QQ(1/2) * abs(sage.all.matrix([self.v0, -self.v2]).determinant())