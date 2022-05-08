import json
from flask import Flask, request
import redis

app = Flask(__name__)
#rd = redis.Redis(host='127.0.0.1', port = '6422', db=0) #change this later
comet_data = []


@app.route('/data', methods=['POST'])
def load_data():
    """
    This function reads in Near Earth Comets' Orbital Elements data and stores it in the Redis database.
    Returns:
    A string that lets the user know that the data has been read from the file.
    """
 #   rd.set('data', json.dumps(data))
    global comet_data
    with open('b67r-rgxc.json', 'r') as f:
        comet_data = json.load(f)
    return f'Data has been read from file\n'

@app.route('/data', methods= ['GET'])
def read_data():
    """
    This function takes the Near Earth Comets' Orbital Elements data that has been loaded as a key and returns it as a JSON list.
    Returns:
    The JSON list of the Near Earth Comets' Orbital Elements data.
    """
    comet_data_dict = {}
    comet_data_dict['comets'] = []
    for i in range(len(comet_data)):
        comet_data_dict['comets'].append(comet_data[i])
    return(comet_data_dict)

@app.route('/comets/<comet>', methods= ["GET"])
def get_comets(comet):
    return(comet_data[4])

@app.route('/download/<jobid>', methods=['GET'])
def download(jobid):
    path = f'/app/{jobid}.png'
    with open(path, 'wb') as f:
        f.write(rd.hget(jobid, 'image'))
    return send_file(path, mimetype='image/png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
