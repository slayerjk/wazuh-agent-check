"""
Main applications functions
"""
from subprocess import run, PIPE
from re import sub, findall
from csv import DictReader


# GET AGENTS LIST INFO(WITH STATUS)
def get_agents_state(prog):
    """
    Use Wazuh's "/var/ossec/bin/agent_control -l" to get agents info

    :return: list of current Wazuh agents and their state

    Example of 'agent_control -l' output:
        Wazuh agent_control. List of available agents:
            ID: 000, Name: Wazuh-1 (server), IP: 127.0.0.1, Active/Local
            ID: 003, Name: server-1, IP: 10.*.*.*, Active
            ...
            ID: 185, Name: server-2, IP: 10.*.*.*, Active

            List of agentless devices:

    Result successful output:
        [
            ['ID: 000', ' Name: Wazuh-1 (server)', ' IP: 127.0.0.1', ' Active/Local'],
            ['ID: 003', ' Name: server-1', ' IP: 10.*.*.*', ' Active'],
            ['ID: 146', ' Name: server-2', ' IP: 10.*.*.*', ' Disconnected'],
            ...
        ]

    Example of result:
        {'ID': '000', 'Name': 'Wazuh-server-1 (server)', 'IP': '127.0.0.1', 'Status': 'Active/Local'}
        {'ID': '003', 'Name': 'server-1', 'IP': '10.*.*.*', 'Status': 'Active'}
        ***
   """
    process = run([prog, '-l'], stdout=PIPE, universal_newlines=True).stdout
    result = []
    filtered_output = [i.split(',') for i in process.split('\n') if i.strip().startswith('ID:')]
    replace_pattern = r'.+:\s(.+)'
    for item in filtered_output:
        temp_dict = {
            'ID': sub(replace_pattern, r'\1', item[0].strip()),
            'Name': sub(replace_pattern, r'\1', item[1].strip()),
            'IP': sub(replace_pattern, r'\1', item[2].strip()),
            'Status': item[3].strip()
        }
        if temp_dict:
            result.append(temp_dict)
    if not result:
        raise Exception('RESULT OF GETTING AGENT STATE IS EMPTY!')
    return result


# PARSE HOSTS DATA
def parse_hosts_data(file):
    """

    :param file:
    :return:

    Example of DictReader info:
        OrderedDict([('Scope', ''), ('Name', ''), ('IP', ''), ('OS', '')])
        OrderedDict([('Scope', 'XXX'), ('Name', 'server-1'), ('IP', '10.*.*.* \n(10.*.*.* \nи 10.*.*.*)'),
                                                    ('OS', 'Red Hat Enterprise Linux Server release 7.9')])
        OrderedDict([('Scope', 'XXX'), ('Name', 'server-2'), ('IP', '10.*.*.*'), ('OS', 'Oracle Linux 8')])
        ...

    Example of result:
        {'Scope': 'XXX', 'Name': 'server-1', 'IP': ['10.*.*.*', '10.*.*.*', '10.*.*.*'],
                                    'OS': 'Red Hat Enterprise Linux Server release 7.9'}
        {'Scope': 'XXX', 'Name': 'server-2', 'IP': ['10.*.*.*'], 'OS': 'Oracle Linux 8'}
        ...
    """
    ip_pattern = r'\b\d+\.\d+\.\d+\.\d+\b'
    with open(file, encoding='utf-8') as f_in:
        data = DictReader(f_in)
        result = []
        for item in data:
            if item['IP']:
                temp_dict = dict()
                temp_dict['Scope'] = item['Scope']
                temp_dict['Name'] = item['Name']
                temp_dict['IP'] = findall(ip_pattern, item['IP'])
                temp_dict['OS'] = item['OS']
                result.append(temp_dict)
            else:
                continue
        if not result:
            raise Exception('RESULT OF PARSING HOSTS FILE IS EMPTY!')
        return result


# MATCH WAZUH AGENTS & RESULT OF PARSED HOSTS FILE
def match_agents_vs_parsed(wazuh_agents, parsed_result):
    """

    Args:
        wazuh_agents: {'ID': '003', 'Name': 'server-1', 'IP': '10.*.*.*', 'Status': 'Active'}
        parsed_result: {'Scope': 'XXX', 'Name': 'server-2', 'IP': ['10.*.*.*'], 'OS': 'Oracle Linux 8'}

    Returns:
        matched_wazuh_agent
            {'ID': '156', 'Name': 'server-1', 'IP': '10.*.*.*', 'Status': 'Active',
                'Matched IP': ['10.*.*.*', '10.*.*.*', '10.*.*.*'],
                'Parsed Name': 'SERVER-1  (10.*.*.*)', 'Scope': 'XXX'}
        no_wazuh_agent
            {'Scope': 'XXX', 'Name': 'server-2', 'IP': ['10.*.*.*'], 'OS': 'Oracle Linux 8'}
        unknown_wazuh_agent
            {'ID': '003', 'Name': 'server-3', 'IP': '10.*.*.*', 'Status': 'Active'}
    """
    no_wazuh_agent = []
    matched_wazuh_agent = []
    unknown_wazuh_agent = []

    # FINDING SCOPE HOSTS WITH/WITHOUT AGENTS
    for parsed in parsed_result:
        match_count = 0
        for agent in wazuh_agents:
            if agent['IP'] in parsed['IP']:
                agent['Matched IP'] = parsed['IP']
                agent['Parsed Name'] = parsed['Name']
                agent['Scope'] = parsed['Scope']
                matched_wazuh_agent.append(agent)
                match_count += 1
                break
        if not match_count:
            no_wazuh_agent.append(parsed)

    # FINDING AGENTS NOT IN SCOPE
    for agent in wazuh_agents:
        match_count = 0
        for parsed in parsed_result:
            if agent['IP'] in parsed['IP']:
                match_count += 1
                break
        if not match_count:
            unknown_wazuh_agent.append(agent)

    return matched_wazuh_agent, no_wazuh_agent, unknown_wazuh_agent
