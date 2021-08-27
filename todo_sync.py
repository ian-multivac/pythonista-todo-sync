import appex
import json
import os
import reminders
import requests

import datetime as dt


def set_ios_reminder(todo_dict, set_alarm):
    """
    Accepts a todo_dict dictionary to create an iOS reminder on the default calendar, and a Boolean to set alarms one day before due date.
    
    Args:
        todo_dict (dict): dictionary with the following keys:
            title (str): The processed string, stripped of keyword flags and values
            description (str): A markdown string in the format of # file_name\ntitle, 
            file_name (str): The original file name
            due_date (timestamp): Processed DUE keyword flag value
            priority (int): Processed PRIORITY keyword flag value
        set_alarm (bool): True if alarms are to be set, False if no alarm
        
    Returns:
        None
        Sets reminders and alarms directly
    """
    
    # TODO: Allow a user-defined calendar stored in config.json
    # TODO: Allow a user-defined alarm default
    task_calendar = reminders.get_default_calendar()
    output_str = 'iOS reminder added. '
    
    r = reminders.Reminder(task_calendar)
    r.title = todo_dict['title']
    r.notes = todo_dict['description']
    # convert the timestamp stored in the dict
    r.due_date = dt.datetime.fromtimestamp(todo_dict['due_date'] // 1000 )
    # Adjust priority due to differing scales on iOS vs ClickUp; default = Normal, or No Priority
    if todo_dict['priority'] == 3:
        r.priority = 0
    elif todo_dict['priority'] == 4:
        r.priority = 7
    else:
        r.priority = todo_dict['priority']
    if set_alarm == True:
        a = reminders.Alarm()
        a.date = dt.datetime.fromtimestamp(todo_dict['due_date'] // 1000) - dt.timedelta(days=1)
        r.alarms = [a]
        output_str += 'Notification set 1 day prior to due date.'
    r.save()
    #print(output_str)


def create_todo_dict(todo, file_name):
    """
    Returns a todo_data dictionary from a text string. Parses and strips keyword flags 'PRIORITY: ' and 'DUE: '.
    
    Args:
        todo (str): the line of text to parse
        file_name (str): the name of the source file, used as a tag in the request payload
    
    Returns:
        todo_dict (dict): dictionary with the following keys:
            title (str): The processed string, stripped of keyword flags and values
            description (str): A markdown string in the format of # file_name\ntitle, 
            file_name (str): The original file name
            due_date (timestamp): Processed DUE keyword flag value
            priority (int): Processed PRIORITY keyword flag value
    """

    # Define keyword flags to parse from the main text.  These are stripped from the task title, etc.
    priority_flag = 'PRIORITY: '
    due_date_flag = 'DUE: '
    
    # set default priority as Normal; ClickUp supports 1-4, 1 being top priority
    # adjusted again for handling iOS reminders in set_ios_reminders function
    priority = 3
    
    # set default due date as today + 7
    due = int(dt.datetime.timestamp((dt.datetime.now() + dt.timedelta(days=7))) * 1000)
    
    # if the keyword flags exist, find them, strip the text, and assign the value to a variable
    if priority_flag in todo:
        priority = todo[todo.find(priority_flag):todo.find(priority_flag) + len(priority_flag) + 1]
        todo = todo.replace(priority, '')
        priority = priority.replace('PRIORITY: ', '')
    if due_date_flag in todo:
        due_date_str = todo[todo.find(due_date_flag):todo.find(due_date_flag) + len(due_date_flag) + 9]
        todo = todo.replace(due_date_str, '')
        # Split the date to handle the month capitalization
        due_date_str = due_date_str.replace('DUE: ', '').split()
        due_date_str = '{} {} {}'.format(due_date_str[0], due_date_str[1].capitalize(), due_date_str[2])
        
        # Expects the date in DD MMM YY format, ie: 01 Jan 25 == January 01, 2025
        due_date = int(dt.datetime.strptime(due_date_str, '%d %b %y').timestamp() * 1000)
        due = due_date
        
    # Create a description that includes the file_name          
    description = '# File {}\n\n{}'.format(file_name, todo.capitalize())
    
    # TODO: Create a Status keyword flag
    # TODO: Create a Tag keyword flag
    # TODO: Create an Assignee keyword flag
    # TODO: Create a Start Date keyword flag
    todo_dict = {
        'title': todo.capitalize(),
        'description': description,
        'file_name': file_name,
        'due_date': due,
        'priority': priority,
        }
    
    return todo_dict

       
def create_clickup_payload(todo_dict):
    """
    Accepts a todo_dict dictionary and returns a json payload for a ClickUp task request.
    
    Args:
        todo_dict (dict): Dictionary with the following keys:
            title (str): The processed string, stripped of keyword flags and values
            description (str): A markdown string in the format of # file_name\ntitle, 
            file_name (str): The original file name
            due_date (timestamp): Processed DUE keyword flag value
            priority (int): Processed PRIORITY keyword flag value
    
    Returns:            
        payload (str): json.dumps() version to be used as a payload within ClickUp post request
    """   
    # Create the payload, assigning a specific tag for imported scripts
    payload = {
        'name': todo_dict['title'].capitalize(),
        'markdown_description': todo_dict['description'],
        'tags':
            [
                'script_import',
                todo_dict['file_name'],
            ],
        'status': 'To Do',
        'due_date': todo_dict['due_date'],
        'priority': todo_dict['priority'],
        'parent': None,
        'links_to': None,
        'check_required_custom_fields': False
    }
    
    return json.dumps(payload)  
    

def parse_todo_identifier(line):
    """
    Returns a string, striped of any task keyword flags, and a Boolean if a task keyword flag is found within the first several characters of the line. Parses and strips keyword flags '[]', '◦', '☐', and '# TODO: '.  Supports variations for '#todo:'.
    
    Args:
        line (str): the line of text to parse
    
    Returns:
        line (str): original string, stripped of any task keyword flags
        has_identifier: True when a task keyword flag was found.
    """
    
    has_identifier = False
    if line[:2].replace(' ', '') == '[]' or line[:1] == '◦' or line[:1] == '☐' or line[:7].replace(' ', '').lower() == '#todo:':
        has_identifier = True
        line = line.replace('[]', '')
        line = line.replace('◦', '')
        line = line.replace('☐', '')
        if line[:7].replace(' ', '').lower() == '#todo:':
            line = line[8:]
        line = line.strip().capitalize()
            
    return line, has_identifier


def main():
    """
    When passed a named file via iOS Share Sheet, parses the text within and processes keyword flags to create ClickUp tasks.  Optional flags allow iOS reminders with alarms to be created.
    
    Args:
        file (file): a named file (ie, not saved in Notes)
        config.json: pre-configured file in root directory; contains ClickUp auth token, optional ios reminders flags
          
    """
    # Are we actually able to read a file?
    # TODO: Figure out how to handle an iOS Notes app share without exporting it
    if not appex.is_running_extension():
        print('This script is intended to be run from the sharing extension, from a named file.')
        
        return
        
    # Do we have a credentials file?
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        auth_token = config['clickup_token']
        clickup_list_id = config['clickup_list_id']
        set_reminders_flag = config['set_ios_reminders']
        set_alarms_flag = config['set_ios_reminders_alarms']
        
    except FileNotFoundError:
        print('Config file not found. Aborting.')
        
        return
        
    
    # TODO: Handle a folder of files, and loop through the immediate directory
    file = appex.get_file_path()
    file_name = os.path.basename(file)
    
    with open(file,'r', encoding='utf-8') as f:
        text = f.readlines()
    
    todo_list = []
            
    for line in text:
        # handle some basic clean-up before looking for keyword flags
        line = line.strip().replace('\t', '').replace('\n', '')
        line, has_identifier = parse_todo_identifier(line)
        if has_identifier == True and line.strip() != '':
            todo_list.append(line)

    # create a request for each todo, assign it to a specific pre-defined list
    headers = {'Authorization': auth_token, 'Content-Type':'application/json'}
    
    print('Checking {} for todo items'.format(file_name))
    for todo in todo_list:
        todo_dict = create_todo_dict(todo, file_name)
        payload = create_clickup_payload(todo_dict)
        new_task_url = 'https://api.clickup.com/api/v2/list/{}/task'.format(clickup_list_id)
        # send the todo
        r = requests.post(new_task_url, headers=headers, data=payload)
        if set_reminders_flag == True:
            set_ios_reminder(todo_dict, set_alarms_flag)
        print(r.status_code, todo)
        
    print('Created {} new tasks.'.format(len(todo_list)))
    
    # TODO: Update the source file with items that have been sent
    # TODO: Add a keyword flag to parse previously sent items
    # TODO: Set counter for status_code 200 vs errors
    # TODO: Read file path to determine project, and associate the task with the appropriate list / reminders calendar
    
if __name__ == '__main__':
    main()
    
