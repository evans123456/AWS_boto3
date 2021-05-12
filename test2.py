
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("serviceAcc.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# db.collection("runs").add(
#     {"cost":0.001150369644165039,
#     "d":3,
#     "pi_estimate":3.1406679365079366,
#     "q":10000,
#     "r":8,
#     "s":1200000}
# )


docs = db.collection("runs").get()
for doc in docs:
    print(doc.to_dict())