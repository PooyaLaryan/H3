import h3

class HexagonalHierarchicalGeospatialIndexingSystem:

    def Convert_to_H3_cell(self, latitude, longitude, resolution):
        h3_index = h3.latlng_to_cell(latitude, longitude, resolution)
        return h3_index
    
    def Convert_back_to_center(self, h3_index):
        center = h3.cell_to_latlng(h3_index)
        return center
    
    def Get_boundary_of_the_cell(self, h3_index):
        boundary = h3.cell_to_boundary(h3_index)
        return boundary

# latitude = 37.775938728915946
# longitude = -122.41795063018799

# resolution = 9


# # Convert to H3 cell
# h3_index = h3.latlng_to_cell(latitude, longitude, resolution)
# print("H3 Index:", h3_index)

# # Convert back to center
# center = h3.cell_to_latlng(h3_index)
# print("Center:", center)

# Get boundary of the cell (hexagon)
# boundary = h3.cell_to_boundary(h3_index)
# print("Boundary:", boundary)
