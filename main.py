def mac(pattern, filter_grid):
    total = 0
    size = len(pattern)
    for i in range(size):
        for j in range(size):
            total = total + pattern[i][j] * filter_grid[i][j]
    return total

cross_filter = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

x_filter = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
]

cross_pattern = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

x_pattern = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
]

print("십자가 패턴 vs 십자가 필터:", mac(cross_pattern, cross_filter))
print("십자가 패턴 vs X 필터:", mac(cross_pattern, x_filter))
print("X 패턴 vs 십자가 필터:", mac(x_pattern, cross_filter))
print("X 패턴 vs X 필터:", mac(x_pattern, x_filter))