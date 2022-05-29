from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
data = []
class People(Resource):
	def get(self):
		for x in data:
			if x['Data'] == name:
				return x
		return {'Data': None}
	def post(self, name):
		temp = {'Data': name}
		data.append(temp)
		return temp
	def delete(self):
		for ind, x in enumerate(data):
			if x['Data'] == name:
				temp = data.pop(ind)
				return {'Note': 'Deleted'}
api.add_resource(People, '/Name/')
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5450)