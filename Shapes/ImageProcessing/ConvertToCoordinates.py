import numpy as np
from tqdm import tqdm
from Coordinate import Coordinate, Coordinates
from scipy.spatial import cKDTree
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS, BEAM_DIAMETER

def get_coordinates(edges, stiffness):
    """
    Extracts the coordinates of the detected edges.

    Returns:
        Coordinates: The extracted coordinates.

    """
    coordinates = Coordinates()
    visited = np.zeros((len(edges), len(edges[0])))
    canvas_width = 20
    canvas_height = 16
    width = len(edges)
    height = 0 if len(edges) == 0 else len(edges[0])

    for i in tqdm(range(height), desc="Getting Coordinates"):
        for j in range(width):
            if edges[j][i] == 255 and visited[j][i] == 0:
                queue = [(j, i)]
                while queue:
                    x, y = queue.pop(0)
                    if visited[x][y] == 0:
                        visited[x][y] = 1
                        # Scale x and y to fit inside width and height
                        scaled_x = (canvas_width * x) / width
                        scaled_y = (canvas_height * y) / height
                        coordinates.append(Coordinate(scaled_x, scaled_y))

                        # Define the possible offsets for neighboring pixels
                        offsets = [(-1, -1), (-1, 0), (-1, 1),
                                    (0, -1),           (0, 1),
                                    (1, -1),  (1, 0),  (1, 1)]
                        
                        neighbors = []
                        for dx, dy in offsets:
                            nx, ny = x + dx, y + dy

                            # Check if the neighbor is within bounds
                            if 0 <= nx < width - 1 and 0 <= ny < height - 1 and visited[nx][ny] == 0:
                                neighbors.append((nx, ny))

                        for neighbor in neighbors:
                            if edges[neighbor[0]][neighbor[1]] == 255:
                                queue.append(neighbor)

    center = Coordinate(12.5, 12.5)
    rotation = 0
    beam_diameter = BEAM_DIAMETER
    coordinates = ordered_by_nearest_neighbor(coordinates, beam_diameter)
    if len(coordinates) != 0:
        coordinates.normalize(center=center, rotation=rotation, stiffness=stiffness, beam_diameter_mm=beam_diameter)

    return coordinates

def ordered_by_nearest_neighbor(coordinates, beam_diameter):
    min_distance = float(MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS)
    
    # Convert the Coordinates object into a list of tuples for easier calculation
    points = [(coord.x, coord.y) for coord in coordinates]
    
    # Initialize the path with the first point
    path = Coordinates()
    path.append(coordinates[0])
    blacklist = set()
    blacklist.add(0)
    
    # Build a k-d tree for efficient nearest neighbor search
    tree = cKDTree(points)

    while True:
        current_coord = path[-1]
        current_point = (current_coord.x, current_coord.y)

        distances, indices = tree.query(current_point, k=len(points), distance_upper_bound=np.inf)        
        next_point_found = False
        for dist, idx in zip(distances, indices):
            # idx == tree.n when there are no more neighbors
            if idx != tree.n and dist >= min_distance and idx not in blacklist:
                # Add the next valid coordinate to the path
                if dist > beam_diameter:
                    coordinates[idx].lp = False
                path.append(coordinates[idx])
                
                # Blacklist all points within distance `m` of the new point
                nearby_indices = tree.query_ball_point(points[idx], min_distance)
                blacklist.update(nearby_indices)

                next_point_found = True
                break

        # If no valid next point is found, break the loop
        if not next_point_found:
            break

    return path