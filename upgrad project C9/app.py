from flask import Flask,redirect,url_for,render_template,request
from flask import Flask, request,jsonify

app=Flask(__name__,template_folder='templates')

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/success/<int:score>')
def success(score):
    res=""
    if score>=50:
        res="PASS"
    else:
        res="FAILURE"
    print("insdie this api")
    return render_template('result.html',result=res)

@app.route('/<int:number>/',methods=['GET'])
def incrementer(number):
    return "Incremented number is " + str(number+1)

### Result checker submit html page
@app.route('/submit',methods=['POST','GET'])
def submit():
    total_score=0
    if request.method=='POST':
        python=float(request.form['python'])
        AI=float(request.form['AI'])
        C=float(request.form['c'])
        data_science=float(request.form['datascience'])
        total_score=(python+AI+C+data_science)/4
    res=""
    return redirect(url_for('success',score=total_score))
    
if __name__=='__main__':
    app.run(debug=True,host="0.0.0.0", port=5400)