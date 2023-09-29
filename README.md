Description
This script automatizes routine of checking hosts scopes vs actual Wazuh agents.

As result you know(using email report and/or log)

what scope hosts don't have Wazuh agent aboard;
what scope hosts match actual Wazuh agents;
what agents among matched agents are Disconnected;
what Wazuh agents are not in scope, but installed

Files:
 * app.py - main file, where functions call
 * app_functions.py - all app functions
 * project_helper.py - some common functions for any app
 * project_mailing.py - e-mail functions
 * project_static.py - vars, logging configs, app sensitive static data, etc
 * script_data/mailing_data.json - data for mailing(required if need email report)
 * script_data/<YOUR SCOPES FILE>.csv - data of your scopes' hosts(REQUIRED)

SCOPES FILE content(csv) example:
```
Scope,Name,IP,OS
COMMON,server-1,192.168.1.101,RHEL 8
DMZ	server-2,192.168.1.102,CentOS 7.9
```

mailing_data.json:
```
{
  "smtp_server": "mail.ex.com",
  "smtp_port": 25,
  "smtp_login": "<YOUR SMTP LOGIN>",
  "smtp_pass": "<YOUR SMTP PASSWORD>",
  "smtp_from_addr": "wazuh@ex.com",
  "list_admins": ["admin1@ex.com", "admin2@.ex.com"],
  "list_users": ["user1@ex.com"]
}
```
