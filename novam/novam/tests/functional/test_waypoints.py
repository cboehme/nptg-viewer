from novam.tests import *

class TestWaypointsController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='waypoints'))
        # Test response...
