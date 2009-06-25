from __future__ import division

import numpy



class four_digits_symmetric:
    def __init__(self, thickness, edge_coeff):
        self.thickness = thickness
        self.edge_coeff = edge_coeff
    
    def __call__(self, x, side):
        t = self.thickness

        y = t * 5 * (0.2969 * numpy.sqrt(x) + ((((-self.edge_coeff * x + 
            0.2843) * x - 0.3516) * x) - 0.126) * x)

        if side == "upper":
            return numpy.array([self.x_upper(x), self.y_upper(y)])
        elif side == "lower":
            return numpy.array([self.x_lower(x), self.y_lower(y)])
        else:
            print "Neither upper nor lower side selected in the call!"
            print "------------------------"

    def y_upper(self, y):
        return y

    def y_lower(self, y):
        return -y

    def x_upper(self, x):
        return x

    def x_lower(self, x):
        return x




class four_digits_cambered:
    def __init__(self, thickness, max_camber, max_camber_pos, edge_coeff):
        self.thickness = thickness
        self.max_camber = max_camber
        self.max_camber_pos = max_camber_pos
        self.edge_coeff = edge_coeff

    def __call__(self, x, side):
        t = self.thickness
        m = self.max_camber
        p = self.max_camber_pos

        y = t * 5 * (0.2969 * numpy.sqrt(x) + ((((-self.edge_coeff * x + 
            0.2843) * x - 0.3516) * x) -0.126) * x)

        if x <= p:
            y_c = m * x / p ** 2 * (2 * p - x)
            theta = numpy.arctan(2 * m / p ** 2 * (p - x))
        else:
            y_c = m * (1 - x) / (1 - p) ** 2 * (1 + x - 2 * p)
            theta = numpy.arctan(m / (1 - p) ** 2 * (2 * p - 2 * x))

        if side == "upper":
            return numpy.array([self.x_upper(x, y, theta), 
                self.y_upper(y_c, y, theta)])
        elif side == "lower":
            return numpy.array([self.x_lower(x, y, theta), 
                self.y_lower(y_c, y, theta)])
        else:
            print "Neither upper nor lower side selected in the call!"
            print "------------------------"

    def y_upper(self, y_c, y, theta):
        return y_c + y * numpy.cos(theta)

    def y_lower(self, y_c, y, theta):
        return y_c - y * numpy.cos(theta)

    def x_upper(self, x, y, theta):
        return x - y * numpy.sin(theta)

    def x_lower(self, x, y, theta):
        return x + y * numpy.sin(theta)




class five_digits:
    def __init__(self, thickness, m, k1, edge_coeff):
        self.thickness = thickness
        self.edge_coeff = edge_coeff
        self.m = m
        self.k1 = k1

    def __call__(self, x, side):
        t = self.thickness
        m = self.m
        k1 = self.k1

        y = t * 5 * (0.2969 * numpy.sqrt(x) + ((((-self.edge_coeff * x + 
            0.2843) * x - 0.3516) * x) -0.126) * x)

        if x <= m:
            y_c = k1 / 6 * x *((x - 3 * m) * x + m ** 2 * (3 - m)) 
            theta = numpy.arctan(k1 / 6 * ((3 * x - 6 * m) * x + 
                m ** 2 * (3 - m)))
        else:
            y_c = k1 * m ** 3 / 6 * (1 - x)
            theta = numpy.arctan(-k1 * m ** 3 / 6)

        if side == "upper":
            return numpy.array([self.x_upper(x, y, theta), 
                self.y_upper(y_c, y, theta)])
        elif side == "lower":
            return numpy.array([self.x_lower(x, y, theta), 
                self.y_lower(y_c, y, theta)])
        else:
            print "Neither upper nor lower side selected in the call!"
            print "------------------------"

    def y_upper(self, y_c, y, theta):
        return y_c + y * numpy.cos(theta)

    def y_lower(self, y_c, y, theta):
        return y_c - y * numpy.cos(theta)

    def x_upper(self, x, y, theta):
        return x - y * numpy.sin(theta)

    def x_lower(self, x, y, theta):
        return x + y * numpy.sin(theta)




def main():
    """
    Program to calculate the coordinates of NACA 4-digit and 5-digit series
    airfoils.

    Set the digits and the number of points to represent the upper and lower
    side of the airfoil in the following lines. Also decide, whether you 
    want a sharp or blunt trailing edge.
    """
    naca_digits = "2412"
    number_of_points = 1000
    sharp_trailing_edge = True

    print "----------------------------"
    print "Airfoil: NACA-%s" %(naca_digits)

    if sharp_trailing_edge == True:
        print "Sharp trailing edge"
        edge_coeff = 0.1036
    else:
        print "Blunt trailing edge"
        edge_coeff = 0.1015

    digits_int = int(naca_digits)
    x = numpy.arange(0, 1+1/number_of_points, 1/number_of_points)
    points_upper = numpy.zeros((len(x),2))
    points_lower = numpy.zeros((len(x),2))

    if len(naca_digits) == 4:
        thickness = (digits_int % 100)
        max_camber_pos = (digits_int % 1000) - thickness
        max_camber = (digits_int % 10000) - max_camber_pos - thickness

        thickness = thickness / 1e2
        max_camber_pos = max_camber_pos / 1e3
        max_camber = max_camber / 1e5

        print "Thickness:", thickness
        print "Position of maximum camber:", max_camber_pos
        print "Maximum camber:", max_camber

        if max_camber == 0 and max_camber_pos == 0:
            print "Symmetric 4-digit airfoil"
            points = four_digits_symmetric(thickness, edge_coeff)
        elif max_camber != 0 and max_camber_pos != 0:
            print "Cambered 4-digit airfoil"
            points = four_digits_cambered(thickness, max_camber, max_camber_pos, 
                edge_coeff)
        else:
            print "You must decide whether your airfoil shall be cambered or not!"
            print "----------------------------"
            raise NotImplementedError

    elif len(naca_digits) == 5:
        thickness = (digits_int % 100)
        max_camber_pos = (digits_int % 10000) - thickness

        thickness = thickness / 1e2
        max_camber_pos = max_camber_pos / 2e4

        print "Thickness:", thickness
        print "Position of maximum camber:", max_camber_pos

        identifier = digits_int // 100
        if identifier == 210:
            m = 0.058
            k1 = 361.4
        elif identifier == 220:
            m = 0.126
            k1 = 51.64
        elif identifier == 230:
            m = 0.2025
            k1 = 15.957
        elif identifier == 240:
            m = 0.29
            k1 = 6.643
        elif identifier == 250:
            m = 0.391
            k1 = 3.23
        else:
            print "5-digit series only implemented for the first three digits in"
            print "210, 220, 230, 240, 250"
            print "----------------------------"
            raise NotImplementedError

        print "5-digit airfoil"
        points = five_digits(thickness, m, k1, edge_coeff)

    else:
        print "Only the 4-digit and 5-digit series are implemented!"
        print "----------------------------"
        raise NotImplementedError

    for i in range(len(x)):
        points_upper[i] = points(x[i], "upper")
        points_lower[i] = points(x[i], "lower")

    filename = "naca-%s.dat" %(naca_digits)
    print "Output file:", filename
    print "----------------------------"
    file = open(filename, "w")
    for pt in list(points_upper) + list(points_lower[::-1]):
        print >>file, "\t".join(repr(p_comp) for p_comp in pt)




if __name__ == "__main__":
    main()
