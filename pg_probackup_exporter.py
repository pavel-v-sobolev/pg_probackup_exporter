#!/usr/bin/python3

# Author: Pavel Sobolev
 

"""
pg_probackup prometheus metrics exporter.
This is a tool for monitoring postgres backups.
It exports pg_probackup metrics as a web service in prometheus format.

To use this program, you need to set 3 environment vars:
 1) path to your pg_probackup executable e.g. 
    PG_PROBACKUP_COMMAND = '/usr/bin/pg_probackup-17'
 2) web service port, default 9899
    PG_PROBACKUP_EXPORTER_PORT = '9899' 
 3) path to backup folder e.g.
    PG_PROBACKUP_PATH = '/mnt/backup'
 4) path to S3 configuration file (optionally)
    PG_PROBACKUP_S3_MINIO_CONFIG = '/etc/pg_probackup/s3.config'
Metrics are available under http://your_host:port/metrics

"""


from flask import Flask
from flask import Response
from datetime import datetime

import os
import json
from json import JSONDecodeError
import sys

cmd = os.environ.get('PG_PROBACKUP_COMMAND')

backup_path = os.environ.get('PG_PROBACKUP_PATH')

minio_config_path = os.environ.get('PG_PROBACKUP_S3_MINIO_CONFIG')

if cmd is None:
    print('ERROR: Need PG_PROBACKUP_COMMAND environment varible')
    sys.exit()
    
if backup_path is None:
    print('ERROR: Need PG_PROBACKUP_PATH environment varible')
    sys.exit()

port = os.environ.get('PG_PROBACKUP_EXPORTER_PORT','9899')

fields = {'id':'id',
          'status':'status',
          'wal':'wal',
          'backup-mode':'backup_mode',
          'compress-alg':'compress_alg',
          'start-time':'start_time',
          'end-time':'end_time',
          'retention-redundancy':'retention_redundancy',
          'retention-window':'retention_window'
          }
    
figures = {'count':'count',
           'error':'error',
           'data-bytes':'data_bytes',
           'wal-bytes':'wal_bytes',
           'uncompressed-bytes':'uncompressed_bytes'}


app = Flask(__name__)

@app.route('/')
def root_folder():
    return 'pg_probackup metrics'

@app.route('/metrics')
def metrics_folder():
    
    # call pg_probackup_command
    show_cmd = f"""{cmd} show --backup-path="{backup_path}" --format=json"""
    if minio_config_path:
        show_cmd = f"{show_cmd} --s3=minio --s3-config-file={minio_config_path}"
    cmd_result = os.popen(show_cmd).read()
    
    try: 
        data = json.loads(cmd_result)
    except JSONDecodeError:
        print(f'ERROR: {show_cmd}\n {cmd_result}')
    
    res_figures = {}    
    for fig in figures:
       	res_figures[fig] = f"# HELP {figures[fig]}\n"
       	res_figures[fig] += f"# TYPE postgres_backup_{figures[fig]} gauge\n"
                
    for d in data:
    	n = 0
    	for b in d['backups']:
            start_time = datetime.strptime(b['start-time'][0:19],'%Y-%m-%d %H:%M:%S')
            status = b['status']
            instance = d['instance']
            
            config_cmd =  f"""{cmd} show-config  --backup-path="{backup_path}" --format=json --instance={instance}"""
            if minio_config_path:
                config_cmd = f"{config_cmd} --s3=minio --s3-config-file={minio_config_path}"
            cmd_result = os.popen(config_cmd).read()
            try:
                config_data = json.loads(cmd_result)
            except JSONDecodeError:
                print(f'ERROR: {config_cmd}\n {cmd_result}')
            
            # append config data to backup data
            b = b | config_data
            
            duration_minutes = 0



            if 'recovery-time' in b:
    	        recovery_time = datetime.strptime(b['recovery-time'][0:19],'%Y-%m-%d %H:%M:%S')
    	        duration_minutes = round((recovery_time - start_time).seconds/60,2)
    	    
            for fig in figures:
                res_figures[fig] += "postgres_backup_" + figures[fig] + "{service_id=\"" + instance + "\""
                
                # add all characteristic fields to figure data
                for fld in fields: 
                    if fld in b:
                        res_figures[fig] += "," + fields[fld] + "=\"" + b[fld] + "\""

                # add backup index                        
                res_figures[fig] += ",backup_no=\"" + ('00' + str(n))[-3:] + "\""
                
                # add backup duration
                res_figures[fig] += ",duration_minutes=\"" + str(duration_minutes) + "\""
                
                if fig == 'count':
                    res_figures[fig] += "} 1\n"
                elif fig == 'error':
                    if status=='ERROR':
                        res_figures[fig] += "} 1\n"
                    else:
                        res_figures[fig] += "} 0\n"
                else:
                    if fig in b:
                        res_figures[fig] += "} " + str(b[fig]) + "\n"
                    else:
                        res_figures[fig] += "} 0\n"
            n+=1
        
    # add all figure data to result
    res = ""			
    for fig in figures:
        res += res_figures[fig]
    			
    return Response(res, mimetype='text/plain')
   

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=port)
