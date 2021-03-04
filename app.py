from flask import Flask,request
import requests
import json
from dateutil.parser import parse
import datetime
import subprocess
import sys
import os
app = Flask(__name__)

def sftp_bash():
    print(os.geteuid(),"current user id in drop in")
    # subprocess.call(["sudo","sftp",'-i','.env/yjkeygoanywhere',"cUCSDHS_WW@its-mft.ucsd.edu"])
    exit_code = subprocess.call(["sudo","sh","./sftpsync.sh",'-i','.env/yjkeygoanywhere','-u','cUCSDHS_WW','-S','./data',
                    '-H','its-mft.ucsd.edu','-R','HS_COVID_WW'])
    message = "All most recent files are dropped" if exit_code else "Successful drop in to the HS_COVID_WW"
    return message

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

@app.route('/',methods = ['GET'])
def drop_in_file():
    today = datetime.date.today()
    prevday = today - datetime.timedelta(days=1)
    date_val = request.args.get('date') or prevday.strftime('%-m/%-d')
    if is_date(date_val): # if the date value inputted is valid
        year = datetime.date.today().year
        name_pattern = datetime.datetime.strptime(date_val,"%m/%d").strftime('%b%-d')
        saved_path = 'data/WW_%s.csv'%(name_pattern)
        r = requests.post('https://4jzevgh86d.execute-api.us-east-1.amazonaws.com/default/traceAPI',
                        data='{"password": "Open, sesame","date":"%s","mode":"drop"}'%date_val,
                        headers={"Content-Type":"application/json"})
        with open(saved_path,'w') as f:
            f.write(json.loads(r.text))
        message = sftp_bash()
        return "Finished File upload for date %s " % date_val + "sftp status: %s" % message
    return "the date entered isn't valid"
if __name__ == '__main__':
    app.secret_key = b'\xb7\xe2\xd6\xa3\xe2\xe0\x11\xd1\x92\xf1\x92G&>\xa2:'
    app.debug = True
    app.run(host='0.0.0.0', port=3002)