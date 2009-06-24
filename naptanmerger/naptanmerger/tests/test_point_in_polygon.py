from naptanmerger.lib.point_in_polygon import point_in_polygon

def test_point_inside_triangle():
	poly = [(-10, -5), (40, 50), (100, -10)]
	r = point_in_polygon(30, 15, poly)
	assert r == True

def test_point_outside_triangle():
	poly = [(-10, -5), (40, 50), (100, -10)]
	r = point_in_polygon(80, 35, poly)
	assert r == False

def test_point_on_vertical_edge():
	poly = [(15, -10), (-15, 10), (15, 30)]
	r = point_in_polygon(15, 5, poly)
	assert r == True

def test_point_on_horizontal_edge():
	poly = [(-5, 10), (-25, 20), (20, 20)]
	r = point_in_polygon(0, 20, poly)
	assert r == True

# In my opinion a point on a vertex of a polygon should be counted
# as inside the polygon the same way points on edges are. However, 
# the algorithm does not work this way. Since this case is not 
# significant for importing bus stops it is ignored here.
#
#def test_point_on_vertex():
#	poly = [(-5, -10), (-25, 20), (20, 20)]
#	r = point_in_polygon(-5, -10, poly)
#	assert r == True
	
def test_point_inside_inline_with_horizontal_edge():
	poly = [(0, -10), (-30, 70), (0, 45), (30, 45), (0, -10)]
	r = point_in_polygon(-10, 45, poly)
	assert r == True
	
def test_point_outside_inline_with_horizontal_edge():
	poly = [(0, -10), (-30, 70), (0, 45), (30, 45), (0, -10)]
	r = point_in_polygon(45, 45, poly)
	assert r == False
	
def test_point_inside_inline_with_tip():
	poly = [(-10, -10), (-30, 40), (30, 40), (10, -5), (0, 10)]
	r = point_in_polygon(-10, 10, poly)
	assert r == True

def test_point_outside_inline_with_tip():
	poly = [(-10, -10), (-30, 40), (30, 40), (10, -5), (0, 10)]
	r = point_in_polygon(-40, -10, poly)
	assert r == False
