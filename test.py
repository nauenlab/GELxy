import matplotlib.pyplot as plt

def calculate_intersection_with_slope(x1, y1, x2, y2, border):
    # Handle vertical lines
    if x1 == x2:
        return (x1, 0 if border == 'bottom' else 25)
    # Handle horizontal lines
    elif y1 == y2:
        return (0 if border == 'left' else 25, y1)
    
    # Calculate slope
    m = (y2 - y1) / (x2 - x1)
    # Calculate y-intercept
    b = y1 - m * x1
    
    if border in ['left', 'right']:
        x = 0 if border == 'left' else 25
        y = m * x + b
        return (x, y)
    else:  # 'top' or 'bottom'
        y = 25 if border == 'top' else 0
        x = (y - b) / m
        return (x, y)

def fix_coordinates_with_corrected_slope(coords):
    fixed_coords = []
    no_lamp_coords = []
    borders = {'left': 0, 'right': 25, 'top': 25, 'bottom': 0}
    
    for i in range(len(coords)):
        if i == 0:  # Add the first point if within bounds
            if 0 <= coords[i][0] <= 25 and 0 <= coords[i][1] <= 25:
                fixed_coords.append(coords[i])
            continue
        
        x1, y1 = coords[i-1]
        x2, y2 = coords[i]

        print(coords[i])
        
        # Check if the segment crosses any border
        for border, value in borders.items():
            if border in ['left', 'right']:
                if (x1 < value < x2) or (x2 < value < x1):
                    intersection = calculate_intersection_with_slope(x1, y1, x2, y2, border)
                    if 0 <= intersection[1] <= 25:
                        fixed_coords.append(intersection)
                        no_lamp_coords.append(intersection)
            else:
                if (y1 < value < y2) or (y2 < value < y1):
                    intersection = calculate_intersection_with_slope(x1, y1, x2, y2, border)
                    if 0 <= intersection[0] <= 25:
                        fixed_coords.append(intersection)
                        no_lamp_coords.append(intersection)
                    
        
        # Add the second point if it's within bounds and no segment was added
        if 0 <= x2 <= 25 and 0 <= y2 <= 25:
            fixed_coords.append((x2, y2))
    
    return fixed_coords, no_lamp_coords


# Example shape with points going out of bounds
shape = [(22, 2), (28, 10), (20, 20), (10, 30), (5, 5), (-5, 10), (10, 10), (1, 5), (-2, -2), (4, -5), (10, 2), (30, 30), (25, 25), (18, 25), (18, 18)]
# shape = [(2.5, -1.66666666666), (0, 3.33333333333333), (-2.5, -1.6666666666), (2.5, -1.66666666666)]
fixed_shape, no_l_c = fix_coordinates_with_corrected_slope(shape)
print("Fixed Shape:", fixed_shape)

bounds = [(0, 0), (0, 25), (25, 25), (25, 0), (0, 0)]
plt.plot(*zip(*bounds), marker='o', color='g', ls='-')
plt.plot(*zip(*shape), marker='o', color='r', ls='-')
plt.plot(*zip(*fixed_shape), marker='o', color='b', ls=':')
# plt.plot(*zip(*no_l_c), marker='o', color='y', ls=':')


plt.show()

