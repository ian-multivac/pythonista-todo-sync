# Pythonista Todo List Sync
A simple Pythonista (iOS) script to parse text files and sync TODO items to ClickUp and iOS reminders.

## About This Project

Todo list apps are a dime a dozen, and I often find myself hopping from one to another, depending on the project that I'm working on.  Lately, I've been using Pythonista 3 on iOS a lot for prototyping small projects while I'm away from my desk.  It has several really useful iOS-specific libraries that have been simple to use, but it's challenging to swap back and forth between apps to update tasks or make notes.

I also use several iPad apps to take notes that allow me to use Apple's Pencil to scrawl out handwritten text and diagrams, and I generally export those to iCloud folders.  They usually contain a lot of items that I jot down to follow up with, but they can easily get lost in the shuffle.  It can be painful.

This script will use the Share sheet within iOS, and process a text file line by line, looking for todo list items and keywords.  If it finds them, it will create a new ClickUp task and iOS reminder item for each one, so I can more easily keep track of where I left off.

[Documentation Page](https://github.mymultivac.com/pythonista-todo/)


### Built With

* [Pythonista3](http://omz-software.com/pythonista/)
  * Pythonista is an iOS-based Python IDE --at the time of writing, it is a paid app.
* [ClickUp](https://clickup.com)
  * ClickUp is a task / project / document manager that has a use-case for everyone.  I prefer it over Notion.


## Getting Started

### Prerequisites

While there is no code to install to use this script, you will require Pythonista 3 in order to use the iOS-specific libraries that come with that app.  This script specifically creates tasks using ClickUp's API, and you will require a few IDs from that platform as well.

### Installation & Configuration

Import the `todo-sync.py` and `config.json.example` files into a folder within Pythonista.  Add the `todo-sync.py` script to a Share sheet shortcut --see Pythonista's documentation for this here: [Utilities for Pythonista's App Extensions](https://omz-software.com/pythonista/docs/ios/appex.html).  See the Usage section below for more details about the required text structures.

Rename the `config.json.example` file to `config.json`.  Ensure that this file is stored in the same folder as the `todo_sync.py` script.

This file should look similar to the following:

```json
{
    "clickup_token": "pk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "clickup_list_id": 87654321,
    "set_ios_reminders": true,
    "set_ios_reminders_alarms": true
}
```

You will need to provide a key for both, `clickup_token` and `clickup_list_id` in order for the script to function correctly.

#### ClickUp Personal API Key

If you don't already have a ClickUp account, you will need to sign up for that first.  Once you do have an account, please review ClickUp's article to find your Personal API Key [Getting Started with the ClickUp API](https://docs.clickup.com/en/articles/1367130-getting-started-with-the-clickup-api).

Use this key for the `clickup_token`.

#### ClickUp List ID

By default, this script will place all tasks into a single list.  You will need to create this list within ClickUp first, and copy the list ID to include in the `config.json` file.

1. Create a new list within ClickUp (you can name it whatever you like)
2. Open the list
3. In the address bar of your browser, copy the list ID portion of the URL:
   1. https://app.clickup.com/12345678/v/l/li/`87654321`

Any tasks created by the script will be added to this list.

#### Set iOS Reminders

If you wish, you can enable or disable setting iOS reminders for any tasks created.  When `set_ios_reminders` is set to `true`, the script will prompt you to authorize Pythonista to use your reminders.  You must allow this, or something will probably explode into error messages.  If it's set to `false`, no iOS reminders will be set.

#### Set iOS Reminders Alarms

If you'd like to have notifications before your reminder's due date, set the `set_ios_reminders_alarms` flag to `true`.  If this is `false`, you can still add reminders for your tasks, but you won't get a pop-up notification before the due date.

## Usage

Before you'll be able to use this script for the first time, there are several configuration steps that are required.  You will also need to review how this script parses keyword flags within your text files, to ensure your tasks are picked up.

### Structuring Your TODO Text

*NOTE: This has really only been used for fairly small .txt and .py files, and may have untested limitations*

The script will read the contents of your file, and look for keyword flags.  In order to be identified as a TODO item, the task must include one of the following flags:

* `# TODO:`
* `[]`
* `◦` <- this is the default character used when exporting iOS Notes as text files
* `☐`

Capitalization and spacing shouldn't matter, but these characters must appear at the beginning of the line (tabs and spaces are stripped).

If a TODO item is found, the script will also parse any other supported keyword flags, to add context to the task to be created.  Supported keyword flags are:

| Keyword Flag | Expected Value Type | Example | Notes |
|:------------:|:-------------------:|:------:|:--------|
| `PRIORITY: ` | integer: 1, 2, 3 or 4 | PRIORITY: 3 | 1 - highest, 4 - lowest |
| `DUE: ` | date: DD MMM YY | DUE: 01 Jan 25 | The month isn't case sensitive, but the day should be padded (%d %b %y format)

**NOTE: The keyword flags ARE case-sensitive, and include a space after the colon**

Any keyword flags, and their values, are stripped from the text before a task is created.  The remaining text will be used as the task's title, and the description will include the name of the file as well.  Within ClickUp, the task will also contain a tag for the file name, to allow for further sorting and filtering.

For example, lines 2, 3 and 5 in the example below will be flagged and processed.

```
How do I need to structure my text?
[] Make sure it has one of the TODO keyword flags
	◦	View the new tasks within ClickUp DUE: 01 Sep 21
This line won't get picked up, but the one below will.
    # TODO: Allow a user-defined calendar stored in config.json PRIORITY: 3
```

### Processing Files

In order to pass your files to the script, navigate to the file within iOS.  This should work from nearly anywhere there is a Share button --with the exception of directly within the Notes app (see below for more info).  You will need to add the script to the Share sheet, following Pythonista's instructions, linked above.  The steps below assume your file is available within the Files app:

1. Long-press on the file.
2. Select Share
3. Select Run Pythonista Script
4. Select the Todo Sync script

That's it!  The file will be parsed, and you should see new ClickUp tasks and reminders set when reviewing those apps.

### Additional Notes

#### iOS Notes App

The Notes app doesn't provide a file name to the Share sheet, until the Note is exported.  This means that any Notes that you'd like to sync should be exported first, and saved somewhere on your local device.  You can then process them through the Files app, for example.

#### Pythonista App

My primary use of this has been to send my `# TODO:` comment lines in a script file as tasks.  This can be done directly within Pythonista, by opening the left-hand panel, and choosing **Edit > Share** to open the Share sheet.  It won't update TODO items that you remove, though, but that may be a future addition.

<!-- ROADMAP -->
## Roadmap

See the # TODO entries within the script itself for more detail.  Primarily this is functional 'as-is', but further work can be done to improve certain areas.

- Updating the TODOs within the source file to include a Task ID, to track that they have been sent previously
- Config options for default reminder alarms
- Adding keyword flags for STATUS, ASSIGNEE and START DATE
- Support for project-based lists, based on the file path
- Generalizing the tasks to allow for further task-manager support within:
  - JIRA
  - GitHub
  - Google Task
- Allowing a folder to be passed, to read each file within

## License

Distributed under the MIT License. See `LICENSE` for more information.


## Contact

Ian - ian@mymultivac.com

Project Link: [https://github.com/ian-multivac/pythonista-todo-sync](https://github.com/ian-multivac/pythonista-todo-sync)
