from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import numpy
from six.moves import range


class FourDigitsSymmetric:
    def __init__(self, thickness, edge_coeff):
        self.thickness = thickness
        self.edge_coeff = edge_coeff

    def __call__(self, x, side):
        t = self.thickness

        def y_upper(y):
            return y

        def y_lower(y):
            return -y

        def x_upper(x):
            return x

        def x_lower(x):
            return x

        y = t * 5 * (0.2969 * numpy.sqrt(x) + ((((-self.edge_coeff * x +
            0.2843) * x - 0.3516) * x) - 0.126) * x)

        if side == "upper":
            return numpy.array([x_upper(x), y_upper(y)])
        elif side == "lower":
            return numpy.array([x_lower(x), y_lower(y)])
        else:
            raise ValueError("Neither upper nor lower side selected in the call.")


class FourDigitsCambered:
    def __init__(self, thickness, max_camber, max_camber_pos, edge_coeff):
        self.thickness = thickness
        self.max_camber = max_camber
        self.max_camber_pos = max_camber_pos
        self.edge_coeff = edge_coeff

    def __call__(self, x, side):
        t = self.thickness
        m = self.max_camber
        p = self.max_camber_pos

        def y_upper(y_c, y, theta):
            return y_c + y * numpy.cos(theta)

        def y_lower(y_c, y, theta):
            return y_c - y * numpy.cos(theta)

        def x_upper(x, y, theta):
            return x - y * numpy.sin(theta)

        def x_lower(x, y, theta):
            return x + y * numpy.sin(theta)

        y = t * 5 * (0.2969 * numpy.sqrt(x) + ((((-self.edge_coeff * x +
            0.2843) * x - 0.3516) * x) - 0.126) * x)

        if x <= p:
            y_c = m * x / p ** 2 * (2 * p - x)
            theta = numpy.arctan(2 * m / p ** 2 * (p - x))
        else:
            y_c = m * (1 - x) / (1 - p) ** 2 * (1 + x - 2 * p)
            theta = numpy.arctan(m / (1 - p) ** 2 * (2 * p - 2 * x))

        if side == "upper":
            return numpy.array([x_upper(x, y, theta), y_upper(y_c, y, theta)])
        elif side == "lower":
            return numpy.array([x_lower(x, y, theta), y_lower(y_c, y, theta)])
        else:
            raise ValueError("Neither upper nor lower side selected in the call.")


class FiveDigits:
    def __init__(self, thickness, m, k1, edge_coeff):
        self.thickness = thickness
        self.edge_coeff = edge_coeff
        self.m = m
        self.k1 = k1

    def __call__(self, x, side):
        t = self.thickness
        m = self.m
        k1 = self.k1

        def y_upper(y_c, y, theta):
            return y_c + y * numpy.cos(theta)

        def y_lower(y_c, y, theta):
            return y_c - y * numpy.cos(theta)

        def x_upper(x, y, theta):
            return x - y * numpy.sin(theta)

        def x_lower(x, y, theta):
            return x + y * numpy.sin(theta)

        y = t * 5 * (0.2969 * numpy.sqrt(x) + ((((-self.edge_coeff * x +
            0.2843) * x - 0.3516) * x) - 0.126) * x)

        if x <= m:
            y_c = k1 / 6 * x * ((x - 3 * m) * x + m ** 2 * (3 - m))
            theta = numpy.arctan(k1 / 6 * ((3 * x - 6 * m) * x +
                m ** 2 * (3 - m)))
        else:
            y_c = k1 * m ** 3 / 6 * (1 - x)
            theta = numpy.arctan(-k1 * m ** 3 / 6)

        if side == "upper":
            return numpy.array([x_upper(x, y, theta), y_upper(y_c, y, theta)])
        elif side == "lower":
            return numpy.array([x_lower(x, y, theta), y_lower(y_c, y, theta)])
        else:
            raise ValueError("Neither upper nor lower side selected in the call.")


def get_naca_points(naca_digits, number_of_points=100,
        sharp_trailing_edge=True,
        abscissa_map=lambda x: 0.03*x+0.97*x**2,
        verbose=False):
    """
    Return a list of coordinates of NACA 4-digit and 5-digit series
    airfoils.
    """

    if verbose:
        def explain(*s):
            print(" ".join(str(s_i) for s_i in s))
    else:
        def explain(*s):
            pass

    explain("Airfoil: NACA-%s" % naca_digits)

    if sharp_trailing_edge:
        explain("Sharp trailing edge")
        edge_coeff = 0.1036
    else:
        explain("Blunt trailing edge")
        edge_coeff = 0.1015

    raw_abscissae = numpy.linspace(0, 1, number_of_points, endpoint=True)
    abscissae = numpy.empty_like(raw_abscissae)
    for i in range(number_of_points):
        abscissae[i] = abscissa_map(raw_abscissae[i])

    digits_int = int(naca_digits)
    if len(naca_digits) == 4:
        thickness = (digits_int % 100)
        max_camber_pos = (digits_int % 1000) - thickness
        max_camber = (digits_int % 10000) - max_camber_pos - thickness

        thickness = thickness / 1e2
        max_camber_pos = max_camber_pos / 1e3
        max_camber = max_camber / 1e5

        explain("Thickness:", thickness)
        explain("Position of maximum camber:", max_camber_pos)
        explain("Maximum camber:", max_camber)

        if max_camber == 0 and max_camber_pos == 0:
            explain("Symmetric 4-digit airfoil")
            points = FourDigitsSymmetric(thickness, edge_coeff)
        elif max_camber != 0 and max_camber_pos != 0:
            explain("Cambered 4-digit airfoil")
            points = FourDigitsCambered(thickness, max_camber,
                    max_camber_pos, edge_coeff)
        else:
            raise NotImplementedError(
                    "You must decide whether your airfoil shall be cambered or not!")

    elif len(naca_digits) == 5:
        thickness = (digits_int % 100)
        max_camber_pos = (digits_int % 10000) - thickness

        thickness = thickness / 1e2
        max_camber_pos = max_camber_pos / 2e4

        explain("Thickness:", thickness)
        explain("Position of maximum camber:", max_camber_pos)

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
            raise NotImplementedError("5-digit series only implemented for "
                    "the first three digits in 210, 220, 230, 240, 250!")

        explain("5-digit airfoil")
        points = FiveDigits(thickness, m, k1, edge_coeff)

    else:
        raise NotImplementedError(
                "Only the 4-digit and 5-digit series are implemented!")

    points_upper = numpy.zeros((len(abscissae), 2))
    points_lower = numpy.zeros((len(abscissae), 2))

    for i in range(len(abscissae)):
        points_upper[i] = points(abscissae[i], "upper")
        points_lower[i] = points(abscissae[i], "lower")

    if sharp_trailing_edge:
        return list(points_upper)[1:-1] + list(points_lower[::-1])
    else:
        return list(points_upper)[1:] + list(points_lower[::-1])


def write_points(points, filename):
    file = open(filename, "w")
    for pt in points:
        print("\t".join(repr(p_comp) for p_comp in pt), file=file)


def main():
    from optparse import OptionParser

    parser = OptionParser(usage="%prog AIRFOIL-ID")
    parser.add_option("-o", "--output",
            help="write ouput to FILE", metavar="FILE")
    parser.add_option("-p", "--points", type="int",
            help="generate N points", metavar="N")
    parser.add_option("-s", "--sharp-trailing-edge", action="store_true")
    parser.add_option("-u", "--uniform-distribution", action="store_true")
    parser.add_option("-q", "--quiet",
            action="store_false", dest="verbose", default=True,
            help="Don't print status messages to stdout")

    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        return

    if options.points is None:
        options.points = 100

    digits = args[0]
    points = get_naca_points(digits,
            number_of_points=options.points,
            sharp_trailing_edge=options.sharp_trailing_edge,
            uniform_distribution=options.uniform_distribution,
            verbose=options.verbose)

    if options.output is None:
        options.output = "naca-%s.dat" % digits

    print("Output file:", options.output)
    write_points(points, options.output)


if __name__ == "__main__":
    main()
