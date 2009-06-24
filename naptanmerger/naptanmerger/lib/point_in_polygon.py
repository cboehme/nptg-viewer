def point_in_polygon(x, y, polygon):

	n = len(polygon)
	inside = False

	p1x, p1y = polygon[0]
	for i in range(1, n+1):
		p2x, p2y = polygon[i % n]
		if y > min(p1y, p2y) and y <= max(p1y, p2y):
			if x <= max(p1x, p2x):
				if p1y != p2y:
					inter_x = float(p2x - p1x) / (p2y - p1y) * (y - p1y) + p1x
  					if x <= inter_x:
						inside = not inside
		p1x, p1y = p2x, p2y

	return inside
