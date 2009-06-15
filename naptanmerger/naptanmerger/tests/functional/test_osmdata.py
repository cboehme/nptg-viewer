from naptanmerger.tests import *

class TestOsmdataController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='OSMData'))
        # Test response...
