class WriteError(RuntimeError):
    pass

class ReadError(RuntimeError):
    pass

class StoreError(RuntimeError):
    pass
    
class Store():    
    def add(self, title):
        pass

#    def commit(self):
#        pass
        
    def delete(self):
        # Delete *selected* note
        pass
        
    def get(self):
        # Gets *selected* note text
        pass
        
#    def mass_update(self, ???):
#        pass
        
    def query(self, text):
        pass

    def rename(self, newtitle):
        # Renames *selected* note to newtitle
        pass
        
    def select(self, uid):
        pass

    def tag(self, tag):
        # Tags *selected* note
        pass
    
    def unselect(self):
        pass
        
    def update(self, text):
        # Updates *selected* note
        pass

