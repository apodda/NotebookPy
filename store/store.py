class WriteError(RuntimeError):
    pass

class ReadError(RuntimeError):
    pass

class StoreError(RuntimeError):
    pass
    
class Store():
    def update_note(self, text, uid):
        pass
    
    def query(self, text):
        pass
    
    def commit(self):
        pass
    
    def get_text(self, uid):
        pass
        
    def add_note(self, text):
        pass
        
    def add_notes(self, text):
        pass
    
    def delete_note(self, uid):
        pass
