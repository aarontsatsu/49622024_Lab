import json
from flask import Flask, request, jsonify


app = Flask(__name__)

"""
    Voters Resource
"""
@app.route('/voters', methods=['GET'])
def get_voters():
    with open('./tmp/voter_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        result = []
        for record in records:
            result.append(record)
        if len(result) > 0:
            return jsonify(result), 200
        return jsonify({'error': 'data not found'}), 404
    
@app.route('/voters/<int:voter_id>', methods=['GET'])
def get_voters_byID(voter_id):
    with open('./tmp/voter_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        for record in records:
            if voter_id == record['id']:
                return jsonify(record), 200
        return jsonify({'message': 'Voter ID not found'}), 404

@app.route('/voters', methods=['POST'])
def create_voter():
    record = json.loads(request.data)

    with open('./tmp/voter_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)

    for r in records:
        if r['id'] == record['id']:
            return jsonify({'message':f'User with id {record["id"]} already exists.'}), 400
        if r['email'] == record['email']:
            return jsonify({'message':f'User with email {record["email"]} already exists.'}), 400
    
    records.append(record), 201

    with open('./tmp/voter_data.txt', 'w') as f:
        f.write(json.dumps(records, indent=2))
    return jsonify(record)

@app.route('/voters/<int:voter_id>', methods=['PATCH'])
def update_voter(voter_id):
    with open('./tmp/voter_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)

        for record in records:
            if record['id'] == voter_id:
                if 'name' in request.json:
                    record['name'] = request.json['name']
                if 'email' in request.json:
                    # check if the updated email already exists
                    updated_email = request.json['email']
                    for r in records:
                        if r['email'] == updated_email and r['id'] != voter_id:
                            return jsonify({"error":f"Email {updated_email} already exists"}), 400
                    record['email'] = request.json['email']
                if 'class' in request.json:
                    record['class'] = request.json['class']
                with open('./tmp/voter_data.txt', 'w') as f:
                    f.write(json.dumps(records, indent=2))
                return jsonify(record), 200
        return jsonify({"error":f"Voter with ID {voter_id} not found"}), 404
                
@app.route('/voters/<int:voter_id>', methods=['DELETE'])
def delete_voter(voter_id):
    new_records = []
    with open('./tmp/voter_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        voter_found = False

        for r in records:
            if r['id'] == voter_id:
                voter_found = True
                continue
            new_records.append(r)
        if not voter_found:
            return jsonify({"error":f"Voter with ID {voter_id} not found"}), 400

    with open('./tmp/voter_data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify({"message":f"Voter {voter_id} deleted successfully"}), 204


"""
    Elections Resource
"""
@app.route('/elections', methods=['GET'])
def get_elections():
    with open('./tmp/election_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        results = []

        for record in records:
            results.append(record)
        if len(results) > 0:
            return jsonify(results), 200
        return jsonify({"error":"No elections found"}), 404

@app.route('/elections/<string:election_id>', methods=['GET'])
def get_election_byID(election_id):
    with open('./tmp/election_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        
        for record in records:
            if election_id in str(record['id']):
                return jsonify(record), 200
        return jsonify({"error":f"Election with ID {election_id} not found"}), 404

@app.route('/elections', methods=['POST'])
def create_election():
    record = json.loads(request.data)

    with open('./tmp/election_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
    
    for i in records:
        if i["id"] in str(record["id"]):
            return jsonify({'message':f'Election with ID {records["id"]} already exists.'})
    records.append(record)

    with open('./tmp/election_data.txt', 'w') as f:
        f.write(json.dumps(records, indent=2))
    return jsonify(record)

# vote in an election
"""
    Implementation Style: A user successfully votes if they are able to get their user_id into the 'voters' field of an election.
    Duplicates are not allowed. 
"""
@app.route('/elections/<string:election_id>', methods=['POST'])
def vote_in_election(election_id):
    with open('./tmp/election_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)

    for record in records:
        if election_id in str(record['id']): #checks if the election ID provided exists
            voters = record['voters']
            num_voters = len(voters) #keeps track of the total number of voters in an election

            for voter in request.json['voters']:
                if any(voter['voter_id'] == v['voter_id'] for v in voters):
                    return jsonify({"error":f"Voter with ID {voter['voter_id']} has already voted."}), 400
                voters.append(voter)
                num_voters +=1

            # update the value of totalVoters to include the new vote casted
            record['totalVoters'] = num_voters
            with open('./tmp/election_data.txt', 'w') as f:
                f.write(json.dumps(records, indent=2))
            return jsonify({"message":f"You have voted successfully"}), 200
    return jsonify({"error":f"Election with ID {election_id} not found"}), 404

@app.route('/elections/<string:election_id>', methods=['DELETE'])
def delete_election(election_id):
    new_records = [] #holds the updated data after deletion
    with open('./tmp/election_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        election_found = False

        for record in records:
            if record['id'] in election_id:
                election_found = True
                continue
            new_records.append(record)
        if not election_found:
            return jsonify({"error":f"Election with ID {election_id} not found"}), 404
        
    with open('./tmp/election_data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify({"message":f"Election {election_id} deleted successfully"}), 204

@app.route('/elections/<string:election_id>', methods=['PUT'])
def update_candidates(election_id):
    with open('./tmp/election_data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)

        for record in records:
            if election_id in str(record['id']):
                record['candidates'] = request.json['candidates']

                with open('./tmp/election_data.txt', 'w') as f:
                    f.write(json.dumps(records, indent=2))
                return jsonify({"message":"Election candidates list updated successfully."}), 200
        return jsonify({"error":f"Election with ID {election_id} not found"}), 404



app.run(debug=True)