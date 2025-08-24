import os

import pywintypes
import win32com.client
from datetime import datetime


def create_task(task_name) -> bool:
    """
    Создание задачи на вызов программы в момент блокировки экрана
    :param task_name: Имя задачи
    """
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    root_folder = _get_root_folder()

    task_def = scheduler.NewTask(0)

    task_def.RegistrationInfo.Author = "Author Name"
    task_def.RegistrationInfo.Description  = "Task will execute Notepad when a " \

    TASK_TRIGGER_SESSION_STATE_CHANGE = 11
    TASK_SESSION_LOCK = 7  # Код события блокировки станции
    trigger = task_def.Triggers.Create(TASK_TRIGGER_SESSION_STATE_CHANGE)
    trigger.StartBoundary = datetime.now().isoformat()
    trigger.StateChange = TASK_SESSION_LOCK

    # Создаем действие
    TASK_ACTION_EXEC = 0
    action = task_def.Actions.Create(TASK_ACTION_EXEC)
    action.Path = os.path.abspath('test.bat')
    action.Arguments = f''

    task_def.Settings.Enabled = True
    task_def.Settings.StartWhenAvailable = True

    try:
        root_folder.RegisterTaskDefinition(
            task_name,
            task_def,
            6,  # TASK_CREATE_OR_UPDATE
            None,  # Имя пользователя (None = текущий)
            None,  # Пароль
            0  # TASK_LOGON_NONE
        )
        return True
    except pywintypes.com_error:
        print('Administrator rights are required to operate')
        return False

def _get_root_folder():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    return scheduler.GetFolder('\\')

def task_exists(task_name) -> bool:
    """
    Проверка, что задача уже создана.
    :param task_name: Имя задачи
    :return:
    """
    try:
        return bool(_get_root_folder().GetTask(task_name))
    except pywintypes.com_error:
        print('Administrator rights are required to operate')
        return False

def delete_task(task_name) -> bool:
    """
    Удалить задачу из планировщика
    :param task_name: Имя задачи
    :return:
    """
    try:
        _get_root_folder().DeleteTask(task_name, 0)
        return True
    except pywintypes.com_error:
        print('Administrator rights are required to operate')
        return False
