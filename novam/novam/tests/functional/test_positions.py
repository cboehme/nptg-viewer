from novam.tests import *

class TestPositionsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='positions', action='index'))
        # Test response...
