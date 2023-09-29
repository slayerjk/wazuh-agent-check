#!/usr/bin/env python3
import logging

# IMPORT PROJECTS PARTS
from project_static import appname, start_date_n_time, logging, logs_dir, logs_to_keep, app_log_name,\
    script_data, agent_control, hosts_data_file

from project_helper import count_estimated_time, files_rotate, check_file, check_create_dir

from app_functions import get_agents_state, parse_hosts_data, match_agents_vs_parsed

# MAILING IMPORTS
from project_static import mailing_data, smtp_server, smtp_port, smtp_login, smtp_pass, smtp_from_addr,\
    mail_list_admins, mail_list_users
from project_mailing import send_mail_report


# SCRIPT STARTED ALERT
logging.info(f'SCRIPT WORK STARTEDED: {appname}')
logging.info(f'Script Starting Date&Time is: {str(start_date_n_time)}')
logging.info('----------------------------\n')


# CHECKING DATA FILES

# CHECK DATA DIR EXISTS/CREATE
check_create_dir(script_data)

# CHECK LOGS DIR EXISTS/CREATE
check_create_dir(logs_dir)

# CHECK DATA FILE EXISTS
logging.info('Checking data file exists')
if not check_file(hosts_data_file):
    logging.error('Data file does not exist, exiting')
    exit()
logging.info('Data file exists, moving on\n')

# CHECK agent_control EXIST
logging.info('CHECKING IF agent_control EXIST')
if not check_file(agent_control):
    logging.error('agent_control DOES NOT EXIST, exiting')
    exit()
logging.info('agent_control EXISTS, moving on')


# GETTING WAZUH AGENT LIST WITH STATUSES
logging.info('STARTED: getting Wazuh agents list')
try:
    wazuh_agents = get_agents_state(agent_control)
except Exception as e:
    logging.error(f'FAILED: getting Wazuh agents list, exiting\n{e}')
    exit()
else:
    logging.info('SUCCEEDED: getting Wazuh agents list\n')


# GETTING ACTIVE/DISCONNECTED AGENTS
logging.info('STARTED: getting active/disconnected agents lists')
active_agents = [i for i in wazuh_agents if i['Status'] == 'Active']
disconnected_agents = [i for i in wazuh_agents if i['Status'] == 'Disconnected']
if not active_agents:
    logging.warning('THERE ARE NO ACTIVE AGENTS IN WAZUH!')
if not disconnected_agents:
    logging.info('THERE ARE NO DISCONNECTED AGENTS IN WAZUH!')
logging.info(f'Wazuh total agents counts(active={len(active_agents)}, disconnected={len(disconnected_agents)}):'
             f' {len(active_agents) + len(disconnected_agents)}')
logging.info('DONE: getting active/disconnected agents lists\n')


# GETTING PARSED RESULT OF HOSTS DATA FILE
logging.info('STARTED: getting parsing result of hosts data')
try:
    parsed_hosts = parse_hosts_data(hosts_data_file)
except Exception as e:
    logging.error(f'FAILED: getting parsing result of hosts data, exiting\n{e}')
    exit()
else:
    total_parsed_hosts = len(parsed_hosts)
    logging.info(f'Total hosts from hosts data file: {total_parsed_hosts}')
    logging.info('DONE: getting parsing result of hosts data\n')


# MATCH WAZUH AGENTS VS PARSED HOSTS FILE
logging.info('STARTED: matching Wazuh agents vs parsed hosts file')
matched_result, not_matched_result, unknown_agents_result = None, None, None
try:
    matched_result, not_matched_result, unknown_agents_result = match_agents_vs_parsed(wazuh_agents, parsed_hosts)
except Exception as e:
    logging.error(f'FAILED: matching Wazuh agents vs parsed hosts file, exiting\n{e}')
else:
    logging.info('DONE: matching Wazuh agents vs parsed hosts file\n')


# MATCHING REPORT
logging.info(f'STARTED: Matching report')
if matched_result:
    logging.info(f'\nTotal Matches are: {len(matched_result)}/{total_parsed_hosts}\n')
    # logging.info('Matched agents are:')
    # [logging.info(match) for match in matched_result]
    matched_disconnected = filter(lambda x: x['Status'] == 'Disconnected', matched_result)
    if matched_disconnected:
        logging.warning(f'\nThere are Disconnected agents in matched result:')
        [logging.warning(item) for item in matched_disconnected]
else:
    logging.warning(f'No Matches at all!')

if not_matched_result:
    logging.info(f'\n\nTotal No Matches are: {len(not_matched_result)}/{total_parsed_hosts}')
    logging.info('No matches for:')
    [logging.info(no_match) for no_match in not_matched_result]
else:
    logging.info('100% match!')

if unknown_agents_result:
    logging.info(f'\n\nTotal Unknown Wazuh agents(Not in Scopes): {len(unknown_agents_result)}')
    logging.info('Unknown agents are:')
    [logging.info(unknown) for unknown in unknown_agents_result]
else:
    logging.info('No Unknown agents!')

logging.info(f'DONE: Matching report\n')

# POST-WORK PROCEDURES

# FINISH JOBS
logging.info('#########################')
logging.info('SUCCEEDED: Script job done!')

logging.info(count_estimated_time(start_date_n_time))
logging.info('----------------------------')
files_rotate(logs_dir, logs_to_keep, app_log_name)

# MAIL REPORT
logging.info('STARTED: sending email report')
try:
    send_mail_report(appname, mail_list_admins, smtp_from_addr, smtp_server, smtp_port, app_log_name, login=None,
                     password=None)
except Exception as e:
    logging.warning(f'FAILED: sending email report\n{e}')
else:
    logging.info('DONE: sending email report')
