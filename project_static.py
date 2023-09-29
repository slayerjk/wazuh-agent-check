"""
- logging settings
- date settings
- static initial project's data
"""

import logging
from datetime import datetime
import json
from csv import DictReader

# COMMON DATA

# SCRIPT APPNAME(FOR SEND MAIL FUNCTION, LOGNAME, ETC)
appname = 'WAZUH-CHECK-AGENTS'

# SCRIPT DATA DIR
'''
By default script uses script's location dir.
If you need custom path for script(sensitive) data, 
set custom_script_data_path = 'yes'
'''
custom_script_data_path = 'no'
if custom_script_data_path == 'yes':
    script_data = '<YOUR ABS PATH>'
else:
    script_data = 'script_data'

# SET TIME TO
start_date_n_time = datetime.now()
start_date = start_date_n_time.strftime('%d-%m-%Y')

# LOGGING SECTION

# LOGS LOCATION
'''
By default script uses script's location dir.
If you need custom path for logs, 
set custom_logs_path = 'yes'
'''
custom_logs_path_option = 'no'
'''
custom logs path example(with your appname in it): 
custom_logs_path =  f'/var/logs/{appname}'
'''
custom_logs_path = '<YOUR ABS PATH FOR SCRIPTS LOGS>'

if custom_logs_path_option == 'yes':
    logs_dir = custom_logs_path
else:
    logs_dir = 'logs'

# LOGS FORMAT
'''
logging_format: is for string of log representation
logging_datefmt: is for representation of %(asctime) param
'''
logging_format = '%(asctime)s - %(levelname)s - %(message)s'
logging_datefmt = '%d-%b-%Y %H:%M:%S'

# LOG FILEMODE
'''
a - for "append" to the end of file
w - create new/rewrite exist
'''
log_filemode = 'w'

# LOGS TO KEEP AFTER ROTATION
logs_to_keep = 30

# DEFINE LOG NAME
app_log_name = f'{logs_dir}/{appname}_{str(start_date)}.log'

# DEFINE LOGGING SETTINGS
logging.basicConfig(filename=app_log_name, filemode=log_filemode, level=logging.INFO,
                    format=logging_format, datefmt=logging_datefmt)

# MAILING DATA
mailing_data = f'{script_data}/mailing_data.json'
with open(mailing_data, encoding='utf-8') as file:
    data = json.load(file)
    smtp_server = data['smtp_server']
    smtp_port = data['smtp_port']
    smtp_login = data['smtp_login']
    smtp_pass = data['smtp_pass']
    smtp_from_addr = data['smtp_from_addr']
    mail_list_admins = data['list_admins']
    mail_list_users = data['list_users']


# VA PROJECT REGARDING DATA
agent_control = '/var/ossec/bin/agent_control'

# SCOPE HOSTS FILE
hosts_data_file = f'{script_data}/ALL-HOSTS-TEST.csv'
