from __future__ import absolute_import
from six.moves import range
from six.moves import zip
def parse_int(it):
    return int(next(it))
def parse_float(it):
    return float(next(it))
class ListParser:
    def __init__(self, len_parser, item_parser):
        self.len_parser = len_parser
        self.item_parser = item_parser

    def __call__(self, it):
        return [self.item_parser(it) for i in range(self.len_parser(it))]

def make_parser(it):
    tp = next(it)
    if tp == "list":
        len_parser = make_parser(it)
        item_parser = make_parser(it)
        return ListParser(len_parser, item_parser)
    elif tp in "float double float32 float64".split():
        return parse_float
    elif tp in "char uchar short ushort int uint int8 uint8 int16 uint16 int32".split():
        return parse_int
    else:
        raise ValueError("unknown type '%s'" % tp)

def parse_ply(name):
    lines = [l.strip().lower() for l in open(name).readlines()]

    assert lines[0] == "ply"
    assert lines[1].split() == ["format", "ascii", "1.0"]
    
    i = 2

    data_queue = []

    # parse header
    while lines[i] != "end_header":
        words = lines[i].split()
        if words[0] == "element":
            i += 1
            props = []
            lsplit = lines[i].split()
            while lsplit[0] == "property":
                props.append((lsplit[-1], make_parser(iter(lsplit[1:-1]))))
                i += 1
                lsplit = lines[i].split()

            data_queue.append((words[1], int(words[2]), props))
        elif words[0] in ["comment", "created"]:
            i += 1
        else:
            raise ValueError("invalid header field")
    i += 1 # skip end_header

    result = {}

    def parse_line(parsers, line):
        it = iter(line.split())
        result = []
        for p in parsers:
            result.append(p(it))
        return result

    from pytools import Record
    class DataBlock(Record):
        pass

    for name, line_count, props in data_queue:
        prop_names, parsers = list(zip(*props))
        result[name] = DataBlock(
                properties=prop_names, 
                data=[parse_line(parsers, l) for l in lines[i:i+line_count]])

        i += line_count

    return result


