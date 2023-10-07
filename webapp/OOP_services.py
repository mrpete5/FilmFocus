


class Service(object):
    ''' Service class to be used by other classes to communicate with the service. '''
    def __init__(self):

        self.service_name = None
        self.is_test_mode = False
        self.is_testdisplay = False
        self.is_poster_game = False
        self.is_testforban = False
        self.is_movie_detail = False
        self.settings = {}

    def set_service_name(self, service_name):  
        self.service_name = service_name
        return self
    
    def get_service_name(self):
        return self.service_name
    
    def set_is_test_mode(self, is_test_mode):
        self.is_test_mode = is_test_mode
        return self
    
    def get_is_test_mode(self):
        return self.is_test_mode

    def test_mode(self, settings):
        if not self.is_test_mode:
            return
        
        
    
    def set_is_testdisplay(self, is_testdisplay):
        self.is_testdisplay = is_testdisplay
        return self
        
        