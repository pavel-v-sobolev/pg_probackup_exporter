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

Metrics are available under _http://your_host:port/metrics_<br />

**Example service file for ubuntu linux:**<br />
_sudo nano /etc/systemd/system/pg_probackup_exporter.service_<br />
<br />
[Service]<br />
Type=simple<br />
User=postgres<br />
Group=postgres<br />
Environment=PG_PROBACKUP_COMMAND='/usr/bin/pg_probackup-17'<br />
Environment=PG_PROBACKUP_PATH='/mnt/backup'<br />
<br />
ExecStart=/usr/bin/python3 /usr/local/bin/pg_probackup_exporter.py<br />
KillMode=control-group<br />
TimeoutSec=5<br />
Restart=on-failure<br />
RestartSec=10<br />
<br />
[Install]<br />
WantedBy=multi-user.target<br />


**Example for prometheus config**<br />
scrape_configs:<br />
\s\s\- job_name: pg_probackup<br />
    scrape_interval: 30s<br />
    scrape_timeout: 30s<br />
    scheme: http<br />
    static_configs:<br />
    \- targets: ["10.8.200.138:9899"]<br />
      labels:<br />
        "service": "postgres"<br />
        "instance": "pg_master"<br />
        "host": "10.8.200.138"<br />
        "Business_Critical": "Medium"<br />
        "Team": "Postgres"<br />

