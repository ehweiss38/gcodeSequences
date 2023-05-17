from flask import Flask,request,Response
app = Flask(__name__)

#tested and works

#launch server: flask --app {filename} run

@app.route('/values', methods=['GET','POST'])
def receiveCoords():
    try:
        if request.method!='POST':
            Exception('Not post')
        print('received')
        if 'locs' in request.get_json():
            locString=request.get_json()['locs']
            print(locString)
            nicksFunction(locString)
            return Response(f'Success: {locString}', status=200)
        else:
            Exception('missing key')
    except Exception as e:
        return Response('Error: {}'.format(str(e)), status=500)
    

def nicksFunction(locs):
    print(locs)
    return 