import argparse
import json
import os
import sys
import tempfile

from screen_generator import gradients_group, type_generator
from tasks import task_exists, delete_task, create_task


def cli():
    parser = argparse.ArgumentParser(
        prog='Lock Screen Changer',
        description='This program will allow you to change the wallpaper on your lock screen every time you log out.',
        epilog='Text at the bottom of help'
    )
    parser.add_argument(
      '-d', '--delete', required=False, action='store_true',
        help='Removing the program from the task scheduler (This will cause it to become inoperable)'
    )
    parser.add_argument(
        '-v', '--vertical', required=False, action=argparse.BooleanOptionalAction,
        help='Vertical wallpaper (default is horizontal)'
    )
    parser.add_argument(
        '-g', '--group', required=False, type=str, default=list(gradients_group.keys())[0],
        help=f'Group gradient wallpaper ({' or '.join(gradients_group.keys())})'
    )
    parser.add_argument(
        '-t', '--type', required=False, type=str, default=list(type_generator.keys())[0],
        help=f'Type of generator ({' or '.join(type_generator.keys())})'
    )

    task_name = 'change_lock_screen'
    args = parser.parse_args()

    if not task_exists(task_name):
        create = input(
            'There is no task in the task scheduler to create a gradient on the lock screen, create. '
            '(Without this, the application will not work) y/n: '
        )
        if create.lower() == 'y':
            create_task(task_name)
            print('Task created.')
        else:
            sys.exit(0)

    if args.delete:
        if task_exists(task_name):
            if delete_task(task_name):
                print(f'Task {task_name} has been deleted.')
                sys.exit(0)
            else:
                print(f'Failed to delete task {task_name}.')
        else:
            print(f'There is no such task in the planning.')

    settings_file_path = tempfile.gettempdir() + '\\settings.json'
    if not os.path.exists(settings_file_path):
        with open(settings_file_path, 'w') as settings_file:
            settings_file.write('{}')

    with open(settings_file_path, 'r') as settings_file:
        settings = json.load(settings_file)

    settings['vertical'] = args.vertical
    settings['group'] = args.group
    settings['type'] = args.type

    print(settings)
    with open(settings_file_path, 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)

    print('Settings updated successfully.')


if __name__ == '__main__':
    cli()