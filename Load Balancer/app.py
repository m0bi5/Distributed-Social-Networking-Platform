#Round Robin Load Balancing
from flask import Flask,request,Response
import requests,logging,sys

app = Flask(__name__)
counter=0

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

dbServers=['http://localhost:5000/','http://localhost:5001/']

def pickServer():
    global counter
    hashId=counter%len(dbServers)
    print('Request routed to server ',hashId,' with url ',dbServers[hashId])
    counter+=1
    return dbServers[hashId]

@app.route('/<path:url>', methods=['GET','POST'])
def balancer(url):
    routeTo=pickServer()
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, routeTo),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0', port=int(sys.argv[1]))
