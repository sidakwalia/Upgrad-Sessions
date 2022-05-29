import json
from flask import Flask, request,jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def query_records():
    name = request.args.get('name')
    print(name)
    with open('data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        for record in records:
            if record['name'] == name:
                return jsonify(record)
        return jsonify({'error': 'data not found'})

@app.route('/', methods=['PUT'])
def create_record():
    record = request.get_json()
    record=record['data']
    with open('data.txt', 'r') as f:
        data = f.read()
        # data=data["name"]
        print("data is--",data)
    records={}
    if not data:
        records = [record]
    else:
        records = json.loads(data)
        print("the record is-",records)
        records=data
    with open('data.txt', 'w') as f:
        f.write(json.dumps(records, indent=2))
    return jsonify(record)

@app.route('/', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    new_records = []
    with open('data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
    for r in records:
        if r['name'] == record['name']:
            r['email'] = record['email']
        new_records.append(r)
    with open('data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(record)
    
@app.route('/', methods=['DELETE'])
def delte_record():
    record = request.get_json()#{"name":"rohit"}
    print("the record is",record)
    new_records = []
    with open('data.txt', 'r') as f:#data.txt {"name":"rohan"}
        data = f.read()
        records = json.loads(data)
        print("the records are----",records)
        for r in records:
            print("the r is----",r)
            if records[str(r)] == record['name']:
                continue
            new_records.append(records[str(r)])
    with open('data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(record)

app.run(debug=True,port=5002)