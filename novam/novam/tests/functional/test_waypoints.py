from novam.tests import *

class TestWaypointsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='waypoints', action='index'))
        # Test response...
