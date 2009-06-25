from __future__ import division

import numpy



class four_digits_sym:
    def __init__(self, length, thickness):
        self.length = length
        self.thickness = thickness
    
    def __call__(self, x, side):
        l = self.length
        t = self.thickness
        x_rel = x / l

        y = l * t * 5 * (0.2969 * numpy.sqrt(x_rel) + ((((-0.1015 * x_rel + 
            0.2843) * x_rel - 0.3516) * x_rel) - 0.126) * x_rel)

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
        return - y

    def x_upper(self, x):
        return x

    def x_lower(self, x):
        return x




class four_digits_cam:
    def __init__(self, length, thickness, max_camber, max_camber_loc):
        self.length = length
        self.thickness = thickness
        self.max_camber = max_camber
        self.max_camber_loc = max_camber_loc

    def __call__(self, x, side):
        l = self.length
        t = self.thickness
        m = self.max_camber
        p = self.max_camber_loc
        x_rel = x / l

        y = l * t * 5 * (0.2969 * numpy.sqrt(x_rel) + ((((-0.1015 * x_rel + 
            0.2843) * x_rel - 0.3516) * x_rel) -0.126) * x_rel)

        if x_rel <= p:
            y_c = m * x_rel * l / p ** 2 * (2 * p - x_rel)
            theta = numpy.arctan(2 * m / p ** 2 * (p - x_rel))
        else:
            y_c = m * l * (1 - x_rel) / (1 - p) ** 2 * (1 + x_rel - 2 * p)
            theta = numpy.arctan(m / (1 - p) ** 2 * (2 * p - 2 * x_rel))

        if side == "upper":
            return numpy.array([self.x_upper(x, y, theta), self.y_upper(y_c, y, theta)])
        elif side == "lower":
            return numpy.array([self.x_lower(x, y, theta), self.y_lower(y_c, y, theta)])
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
    Program to calculate the coordinates of NACA 4-digit series airfoils.

    Set the digits, the number of points to represent the upper and lower 
    side of the airfoil and the length of the airfoil in the following lines.
    """
    naca_digits = "0012"
    number_of_points = 1000
    length = 1

    print "----------------------------"

    if len(naca_digits) != 4:
        print "Only the 4-digit-series is implemented!"
        print "----------------------------"
        raise NotImplementedError

    digits_int = int(naca_digits)
    thickness = (digits_int % 100)
    max_camber_loc = (digits_int % 1000) - thickness
    max_camber = (digits_int % 10000) - max_camber_loc - thickness

    thickness = thickness / 100
    max_camber_loc = max_camber_loc / 1000
    max_camber = max_camber / 100000

    print "Airfoil: NACA-%s" %(naca_digits)
    print "Length:", length
    print "Thickness:", thickness * length
    print "Location of maximum camber:", max_camber_loc * length
    print "Maximum camber:", max_camber * length

    x = numpy.arange(0, length+length/number_of_points, length/number_of_points)
    points_upper = numpy.zeros((len(x),2))
    points_lower = numpy.zeros((len(x),2))

    if max_camber == 0 and max_camber_loc == 0:
        print "Symmetric airfoil"
        points = four_digits_sym(length, thickness)
    elif max_camber != 0 and max_camber_loc != 0:
        print "Cambered airfoil"
        points = four_digits_cam(length, thickness, max_camber, max_camber_loc)
    else:
        print "You must decide whether your airfoil shall be cambered or not!"
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
