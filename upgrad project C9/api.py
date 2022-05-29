from flask import Flask, request,jsonify
#jsonify is defined as a functionality within Python’s capability to c
# convert a json (JavaScript Object Notation) output into a response object with application/json 
# mimetype by wrapping up a dumps( ) function for adding the enhancements. 
app = Flask(__name__)


"""How does jsonify Work in Flask?

During passing single argument, jsonify just passes the parameter as it is to dumps( ) function.
Before passing multiple arguments, jsonify converts the arguments to array before passing it to dumps( ) function.
Before passing multiple keyword arguments, jsonify converts the arguments to a dictionary before passing it to dumps( ) function.
Before passing args and kwargs, jsonify will throw an exception as it is passes to dumps( ) function."""

"""PUT method is idempotent. So if you send retry a request 
multiple times, that should be equivalent to single request modification."""

@app.route('/hello/', methods=['GET', 'POST'])
def welcome():
    return "Hello World!"

@app.route('/sum_no', methods=['GET', 'POST'])
def welcome2():
    a=int(5)
    b=int(6)
    return {"sum":a+b}

@app.route('/calculator', methods=['PUT'])
def welcome3():
    a=int(5)
    b=int(6)
    return {"sum":a+b}


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5400)