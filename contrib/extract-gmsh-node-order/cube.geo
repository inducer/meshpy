Mesh.RecombineAll=1;
Mesh.Recombine3DAll=1;
Mesh.Algorithm = 8;
Mesh.Algorithm3D = 9;
Mesh.Smoothing = 0;

Mesh.ElementOrder = 4;

Point(1) = {0, 0, 0, 3};

line_out[] = Extrude {1,0,0} {
  Point{1}; Recombine;
};
surf_out[] = Extrude {0,1,0} {
  Line{line_out[1]}; Recombine;
};
vol_out[] = Extrude {0,0,1} {
  Surface{surf_out[1]}; Recombine;
};
