from PIL import Image, ImageDraw, ImageFont

from abc import ABC, abstractmethod

class GeneratorWallpaper(ABC):

    def add_text_to_image(
        self,
        image: Image,
        text: str,
        font_size: int,
        font_name: str,
        font_color: tuple[int, int, int] | None = None,
        position: tuple[int, int] = (0, 0),
        invert_location: bool = False
    ):
        draw = ImageDraw.Draw(image)

        try:
            # C:\Windows\Fonts
            font = ImageFont.truetype(font_name, size=font_size)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox(position, text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if invert_location:
            # Вычисляем позицию для центрирования
            position = (
                position[0] - text_width - 1,
                position[1] - text_height - 1
            )

        if font_color is None:
           font_color = self.get_text_color(image, position, text_width, text_height)

        # Добавляем текст на изображение
        draw.text(
            xy=position,
            text=text,
            font=font,
            fill=font_color
        )

        return image

    def get_text_color(self, draw, position, text_width, text_height):
        left_up = draw.getpixel(position)
        right_down = draw.getpixel((position[0] + text_width, position[1] + text_height))

        # TODO: Это не правильный метод, в RGB не евклидова метрика разности цвета для человеческого глаза
        # Для тестов пойдет
        median_color_red = round(abs(left_up[0] - right_down[0]) // 2) + left_up[0]
        median_color_green = round(abs(left_up[1] - right_down[1]) // 2) + left_up[1]
        median_color_blue = round(abs(left_up[2] - right_down[2]) // 2) + left_up[2]

        return self.find_best_text_color((median_color_red, median_color_green, median_color_blue))

    @staticmethod
    def simple_contrast(c1, c2):
        """
        Простой метод вычисления контраста на основе разницы яркости
        """
        r1, g1, b1 = c1
        r2, g2, b2 = c2
        brightness1 = (r1 * 299 + g1 * 587 + b1 * 114) / 1000
        brightness2 = (r2 * 299 + g2 * 587 + b2 * 114) / 1000
        return abs(brightness1 - brightness2)

    def find_best_text_color(self, background_color):
        """
        Определяет лучший цвет текста (черный или белый) для данного фона
        """
        white = (255, 255, 255)
        black = (0, 0, 0)

        white_contrast = self.simple_contrast(background_color, white)
        black_contrast = self.simple_contrast(background_color, black)

        return white if white_contrast > black_contrast else black

    @abstractmethod
    def generator_wallpaper(self, width: int, height: int, orientation: str = 'H', **kwargs) -> Image:
        pass


class GradientGeneratorWallpaper(GeneratorWallpaper):
    def generator_wallpaper(self, width: int, height: int, orientation: str = 'H', **kwargs):

        if 'gradient_colors' not in kwargs:
            raise ValueError('gradient_colors is required')
        else:
            gradient_colors: list[tuple[int, int, int]] = kwargs['gradient_colors']

        if 'slip' not in kwargs:
            slip = None
        else:
            slip: list[float] | None = kwargs['slip']

            if slip is not None and sum(slip) != 1.0:
                raise ValueError('Slip must sum to 1.0')

        image = self._get_gradient_background(width, height, gradient_colors, slip, orientation)

        image = self.add_text_to_image(
            image,
            font_size=28,
            font_name="consola.ttf",
            position=(24, 24),
            text=f'GRADIENT WALLPAPER \n\n{'\n'.join([f'{color[0]:02X}{color[1]:02X}{color[2]:02X}' for color in gradient_colors])}',
        )

        image = self.add_text_to_image(
            image,
            text=f'My github: DoktorTa',
            font_size=28,
            font_name="consola.ttf",
            position=(width - 24, height - 24),
            invert_location=True
        )
        return image

    @staticmethod
    def _get_gradient_background(
        width: int,
        height: int,
        gradient_colors: list[tuple[int, int, int]],
        slip: list[float] | None = None,
        orientation: str = 'H'
    ):
        segment_length = 0

        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        total_length = width if orientation == 'H' else height

        if slip is None:
            segment_length = total_length // (len(gradient_colors) - 1)

        start_pos = 0
        end_pos = 0
        for i in range(len(gradient_colors) - 1):

            if slip is not None:
                segment_length = int(total_length * slip[i])

            # Получаем текущую пару цветов
            color1 = gradient_colors[i]
            color2 = gradient_colors[i + 1]

            # Вычисляем начальную и конечную позицию для текущего сегмента
            end_pos += segment_length

            if i == len(gradient_colors) - 2 and end_pos < total_length:
                end_pos = total_length

            # Создаем градиент между двумя цветами
            for pos in range(start_pos, end_pos):
                # Вычисляем процент прогресса для текущей позиции
                progress = (pos - start_pos) / segment_length

                # Интерполируем цвета
                r = int(color1[0] + (color2[0] - color1[0]) * progress)
                g = int(color1[1] + (color2[1] - color1[1]) * progress)
                b = int(color1[2] + (color2[2] - color1[2]) * progress)

                if orientation == 'H':
                    # Горизонтальный градиент
                    line_coords = [(pos, 0), (pos, height)]
                else:
                    # Вертикальный градиент
                    line_coords = [(0, pos), (width, pos)]

                draw.line(line_coords, fill=(r, g, b))

            start_pos = end_pos

        return image
