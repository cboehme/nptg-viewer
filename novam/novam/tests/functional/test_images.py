from novam.tests import *

class TestImagesController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='images'))
        # Test response...
