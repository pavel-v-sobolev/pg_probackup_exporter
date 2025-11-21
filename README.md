# pg_probackup_exporter


Postgres pg_probackup prometheus metrics exporter.
This is a tool for monitoring postgresql backups.
It exports pg_probackup metrics as a web service in prometheus format.

**Installation**<br />
1) download pg_probackup_exporter.py and put to your folder. E.g. _/usr/local/bin_
2) install python flask library. For ubuntu: _sudo apt install python3-flask_
3) set environment variables and run the program with the following command: _python3 /usr/local/bin/pg_probackup_exporter.py_

**You need to set 3 environment vars:**<br />
 1) path to your pg_probackup executable e.g. 
    PG_PROBACKUP_COMMAND = '/usr/bin/pg_probackup-17'
 2) web service port, default 9899
    PG_PROBACKUP_EXPORTER_PORT = '9899' 
 3) path to backup folder e.g.
    PG_PROBACKUP_PATH = '/mnt/backup'
 4) path to minio config (optionally)
    PG_PROBACKUP_S3_MINIO_CONFIG = '/etc/pg_probackup/s3.config'

Metrics are available under _http://your_host:port/metrics_<br />

**Example service file for ubuntu linux:**<br />
_sudo nano /etc/systemd/system/pg_probackup_exporter.service_<br />
<pre>
[Service]
Type=simple
User=postgres
Group=postgres
Environment=PG_PROBACKUP_COMMAND='/usr/bin/pg_probackup-17'
Environment=PG_PROBACKUP_PATH='/mnt/backup'
Environment=PG_PROBACKUP_S3_MINIO_CONFIG='/etc/pg_probackup/s3.config'
ExecStart=/usr/bin/python3 /usr/local/bin/pg_probackup_exporter.py
KillMode=control-group
TimeoutSec=5
Restart=on-failure
RestartSec=10
[Install]
WantedBy=multi-user.target
</pre>

**Example for prometheus config**<br />
<pre>
scrape_configs:
  - job_name: pg_probackup
    scrape_interval: 30s
    scrape_timeout: 30s
    scheme: http
    static_configs:
    - targets: ["your_host:9899"]
      labels:
        "service": "postgres"
        "instance": "your_host"
        "host": "your_host"
        "Business_Critical": "Medium"
        "Team": "Postgres"

</pre>