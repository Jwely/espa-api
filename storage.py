class DBStorage(Storage):

    def __init__(self, connection):
        self.connection = connection

    def initialize(self):
        with self.connection as cursor:
            with open('schema.sql', 'r') as schema:
                cursor.execute(schema.read())
        
    def login(username, password):
        pass

    def user_info(username):
        pass

    def list_orders(username):
        pass        
