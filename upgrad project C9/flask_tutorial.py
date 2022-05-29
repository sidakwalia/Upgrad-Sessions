# pip install Flask 
# for installing flask
from flask import Flask,request,jsonify

app=Flask(__name__)

@app.route('/api/calculate',methods=['POST'])
def calculator():
    request1=request.get_json()
    num1=request1["num1"]
    num2=request1["num2"]
    return {"sum":num1+num2,"subtraction":num1-num2,"name":'Inderpreet',"Marks":78}

if __name__=='__main__':
    app.run(debug=True,host="0.0.0.0",port=5050)
