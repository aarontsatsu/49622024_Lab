import json
from flask import Flask, request, jsonify
from google.cloud import firestore

#initializing the firestore client with the project ID
db = firestore.Client(project="ashesi-voting-system")

app = Flask(__name__)

"""
    Voters Resource
"""
@app.route('/voters', methods=['GET'])
def get_voters():
    voters_data = db.collection('voters')
    voters = voters_data.stream()
    result = []
    for voter in voters:
        voter_dict = voter.to_dict()
        voter_dict['id'] = voter.id
        result.append(voter_dict)
    if len(result) > 0:
        return jsonify(result), 200
    return jsonify({'error': 'data not found'}), 404
    
@app.route('/voters/<string:voter_id>', methods=['GET'])
def get_voters_byID(voter_id):
    voters_data = db.collection('voters').document(voter_id)
    voter = voters_data.get()

    if voter.exists:
        voter_dict = voter.to_dict()
        voter_dict['id'] = voter.id
        return jsonify(voter_dict), 200
    return jsonify({'message': 'Voter ID not found'}), 404

@app.route('/voters', methods=['POST'])
def create_voter():
    record = json.loads(request.data)

    voters_data = db.collection('voters')
    query_check = voters_data.where('id', '==', record['id'])
    voters = query_check.stream()

    for voter in voters:
        return jsonify({'message':f'User with id {record["id"]} already exists.'}), 400
    
    voter_data = voters_data.document()
    voter_data.set(record)
    record['id'] = voter_data.id

    return jsonify(record), 201

@app.route('/voters/<string:voter_id>', methods=['PATCH'])
def update_voter(voter_id):
    voter_data = db.collection('voters').document(voter_id)
    voter_doc = voter_data.get()
    if not voter_doc.exists:
        return jsonify({"error":f"Voter with ID {voter_id} not found"}), 404

    voter_info = voter_doc.to_dict()
    if 'name' in request.json:
        voter_info['name'] = request.json['name']

    
    if 'email' in request.json:
        updated_email = request.json['email']
        voters_query = db.collection('voters').where('email', '==', updated_email).get()

        for v in voters_query:
            if v.id != voter_id:
                return jsonify({"error":f"Email {updated_email} already exists"}), 400
        voter_info['email'] = updated_email
    
    
    if 'class' in request.json:
        voter_info['class'] = request.json['class']
    
    voter_data.set(voter_info)
    return jsonify(voter_info), 200
                
@app.route('/voters/<string:voter_id>', methods=['DELETE'])
def delete_voter(voter_id):
    voter_data = db.collection('voters').document(voter_id)
    voter_doc = voter_data.get()

    if not voter_doc.exists:
        return jsonify({"error":f"Voter with ID {voter_id} not found"}), 404
    
    voter_data.delete()
    
    return jsonify({"message":f"Voter {voter_id} deleted successfully"}), 204


"""
    Elections Resource
"""
@app.route('/elections', methods=['GET'])
def get_elections():
    elections_data = db.collection('elections')
    elections = elections_data.stream()
    result = []

    for election in elections:
        election_dict = election.to_dict()
        election_dict['id'] = election.id
        result.append(election_dict)
    if len(result) > 0:
        return jsonify(result), 200
    else:
        return jsonify({"error":"No elections found"}), 404

# @app.route('/elections/<string:election_id>', methods=['GET'])
# def get_election_byID(election_id):
#     with open('./tmp/election_data.txt', 'r') as f:
#         data = f.read()
#         records = json.loads(data)
        
#         for record in records:
#             if election_id in str(record['id']):
#                 return jsonify(record), 200
#         return jsonify({"error":f"Election with ID {election_id} not found"}), 404

# @app.route('/elections', methods=['POST'])
# def create_election():
#     record = json.loads(request.data)

#     with open('./tmp/election_data.txt', 'r') as f:
#         data = f.read()
#         records = json.loads(data)
    
#     for i in records:
#         if i["id"] in str(record["id"]):
#             return jsonify({'message':f'Election with ID {records["id"]} already exists.'})
#     records.append(record)

#     with open('./tmp/election_data.txt', 'w') as f:
#         f.write(json.dumps(records, indent=2))
#     return jsonify(record)

# # vote in an election
# """
#     Implementation Style: A user successfully votes if they are able to get their user_id into the 'voters' field of an election.
#     Duplicates are not allowed. 
# """
# @app.route('/elections/<string:election_id>', methods=['POST'])
# def vote_in_election(election_id):
#     with open('./tmp/election_data.txt', 'r') as f:
#         data = f.read()
#         records = json.loads(data)

#     for record in records:
#         if election_id in str(record['id']): #checks if the election ID provided exists
#             voters = record['voters']
#             num_voters = len(voters) #keeps track of the total number of voters in an election

#             for voter in request.json['voters']:
#                 if any(voter['voter_id'] == v['voter_id'] for v in voters):
#                     return jsonify({"error":f"Voter with ID {voter['voter_id']} has already voted."}), 400
#                 voters.append(voter)
#                 num_voters +=1

#             # update the value of totalVoters to include the new vote casted
#             record['totalVoters'] = num_voters
#             with open('./tmp/election_data.txt', 'w') as f:
#                 f.write(json.dumps(records, indent=2))
#             return jsonify({"message":f"You have voted successfully"}), 200
#     return jsonify({"error":f"Election with ID {election_id} not found"}), 404

# @app.route('/elections/<string:election_id>', methods=['DELETE'])
# def delete_election(election_id):
#     new_records = [] #holds the updated data after deletion
#     with open('./tmp/election_data.txt', 'r') as f:
#         data = f.read()
#         records = json.loads(data)
#         election_found = False

#         for record in records:
#             if record['id'] in election_id:
#                 election_found = True
#                 continue
#             new_records.append(record)
#         if not election_found:
#             return jsonify({"error":f"Election with ID {election_id} not found"}), 404
        
#     with open('./tmp/election_data.txt', 'w') as f:
#         f.write(json.dumps(new_records, indent=2))
#     return jsonify({"message":f"Election {election_id} deleted successfully"}), 204

# @app.route('/elections/<string:election_id>', methods=['PUT'])
# def update_candidates(election_id):
#     with open('./tmp/election_data.txt', 'r') as f:
#         data = f.read()
#         records = json.loads(data)

#         for record in records:
#             if election_id in str(record['id']):
#                 record['candidates'] = request.json['candidates']

#                 with open('./tmp/election_data.txt', 'w') as f:
#                     f.write(json.dumps(records, indent=2))
#                 return jsonify({"message":"Election candidates list updated successfully."}), 200
#         return jsonify({"error":f"Election with ID {election_id} not found"}), 404



app.run(debug=True)