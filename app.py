from flask import Flask,request,jsonify, make_response
import requests
import json
import datetime
import subprocess
import sys
import os
app = Flask(__name__)

def generateResponse(elem={}, status=200):
    response = make_response(jsonify(elem), status)
    return response

def sftp_bash():
    print(os.geteuid(),"current user id in drop in")
    # subprocess.call(["sudo","sftp",'-i','.env/yjkeygoanywhere',"cUCSDHS_WW@its-mft.ucsd.edu"])
    exit_code = subprocess.call(["sudo","sh","./sftpsync.sh",'-i','.env/yjkeygoanywhere','-u','cUCSDHS_WW','-S','./data',
                    '-H','its-mft.ucsd.edu','-R','HS_COVID_WW'])
    message = "All most recent files are dropped" if exit_code else "Successful drop in to the HS_COVID_WW"
    return message


@app.route('/',methods = ['GET'])
def drop_in_file():
    today = datetime.date.today()
    prevday = today - datetime.timedelta(days=1)
    date_val = request.args.get('date') or prevday
    try:
        date_val = datetime.datetime.strptime(date_val,"%m/%d%/%y").strftime('%-m/%-d/%-y')
        name_pattern = datetime.datetime.strptime(date_val,"%m/%d/%y").strftime("%b%-d")
        saved_path = 'data/WW_%s.csv'%(name_pattern)
        r = requests.post('https://4jzevgh86d.execute-api.us-east-1.amazonaws.com/default/traceAPI',
                        data='{"password": "Open, sesame","date":"%s","mode":"drop"}'%date_val,
                        headers={"Content-Type":"application/json"})
        if  r.status_code != requests.codes.ok:
            return generateResponse({"message":"fetching drop in files fail, please try again later"},406)
        with open(saved_path,'w') as f:
            f.write(json.loads(r.text))
        sftp_message = sftp_bash()
        return_message = "Finished File upload for date %s " % date_val + "sftp status: %s" % sftp_message
        return generateResponse({"message":return_message})
    except:
        return generateResponse({"message":"the date entered isn't valid"},400)
if __name__ == '__main__':
    app.secret_key = b'\xb7\xe2\xd6\xa3\xe2\xe0\x11\xd1\x92\xf1\x92G&>\xa2:'
    app.debug = True
    app.run(host='0.0.0.0', port=3002)