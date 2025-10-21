from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://ignacio:Database15*@cluster0.mmxuyas.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client['MiProyectoWeb']

# crear la colección "Calendario" si no existe
try:
    if 'Calendario' not in db.list_collection_names():
        db.create_collection('Calendario')
        print('Colección "Calendario" creada.')
    else:
        print('La colección "Calendario" ya existe.')
except Exception as e:
    print('Error al crear la colección:', e)