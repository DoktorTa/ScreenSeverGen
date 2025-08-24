import asyncio
import json

import ctypes
import os
import tempfile

from winrt._winrt_windows_storage import StorageFile
from winrt.windows.system.userprofile import LockScreen

from generator_wallpaper import GradientGeneratorWallpaper
from gradient import RandomGradientGroup, BaseGradientGroup, SkyGradientGroup


async def set_lock_screen(image_path):
    abs_path = os.path.abspath(image_path)
    file = await StorageFile.get_file_from_path_async(abs_path)
    await LockScreen.set_image_file_async(file)


gradients_group = {
    'random': RandomGradientGroup,
    'base': BaseGradientGroup,
    'sky': SkyGradientGroup,
}

type_generator = {
    'gradient': GradientGeneratorWallpaper,
}


if __name__ == "__main__":
    try:
        with open(tempfile.gettempdir() + '\\settings.json', 'r') as settings_file:
            settings = json.load(settings_file)

        generator = type_generator[settings['type']]()
        gradients = gradients_group[settings['group']]()
        orientation = 'V' if settings['vertical'] else 'H'

        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        width *= 2
        height *= 2

        gradient_colors = gradients.get_gradient_color()
        image = generator.generator_wallpaper(width, height, orientation=orientation, gradient_colors=gradient_colors)

        image_path = tempfile.gettempdir() + '\\example.png'
        image.save(image_path)
        asyncio.run(set_lock_screen(image_path))
    except Exception as e:
        print(e)
        input('Press Enter to continue...')