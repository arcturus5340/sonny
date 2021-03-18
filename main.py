from abc import ABC, abstractmethod
import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import typing
import os

import checker
import distortion
import grid
import surface


class VectorPicture:
    def __init__(self):
        self.angle_matrix: typing.Optional[np.ndarray] = None
        self.start_positions_matrix: typing.Optional[np.ndarray] = None
        self.steps_count: typing.Optional[int] = None
        self.steps_length: typing.Optional[int] = None
        self.height: typing.Optional[int] = None
        self.width: typing.Optional[int] = None
        self.surface = None
        self.all_points: list = [[0, 0], [0, 0]]
        self.checkers: list = []
        self.teardown_checkers: list = []

    def show_vector_field(self):
        mpl.rcParams['figure.dpi'] = 300
        x, y = np.meshgrid(np.arange(0, self.width, 1), np.arange(0, self.height, 1))
        u, v = np.vectorize(math.cos)(self.angle_matrix), np.vectorize(math.sin)(self.angle_matrix)
        plt.quiver(x, y, u, v)
        plt.show()

    def __draw_line(self, line_obj, coords):
        x, y = coords
        line_obj.start_point(x, y)
        current_line_points = [[x, y]]
        grid_angle = self.angle_matrix[y][x]
        for i in range(self.steps_count):
            x += self.steps_length * math.cos(grid_angle)
            y += self.steps_length * math.sin(grid_angle)

            check_failed = False
            for checker in self.checkers:
                checker.load(x=x, y=y, all_points=self.all_points)
                if not checker.result():
                    check_failed = True
                    break
            if check_failed:
                break

            line_obj.next_point(x, y)
            current_line_points.append([x, y])
            if 0 >= round(x) or round(x) >= self.width or 0 >= round(y) or round(y) >= self.height:
                break
            grid_angle = self.angle_matrix[round(y)][round(x)]

        check_failed = False
        for checker in self.teardown_checkers:
            checker.load(length=len(current_line_points))
            if not checker.result():
                check_failed = True
                break
        if check_failed:
            return

        self.all_points.extend(current_line_points)
        self.surface.draw(line_obj)

    def draw(self):
        paths = np.full(self.start_positions_matrix.shape[:-1], self.surface.line)
        np.vectorize(self.__draw_line, signature='(),(2)->()')(paths, self.start_positions_matrix)

    def save(self, path):
        self.surface.save(path)


class Builder(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def set_start_positions_matrix(self, matrix: np.ndarray):
        pass

    @abstractmethod
    def set_angle_matrix(self, matrix: np.ndarray):
        pass

    @abstractmethod
    def set_steps_params(self, steps_counts: int, steps_length: int):
        pass

    @abstractmethod
    def set_checker(self, checker: checker.Checker):
        pass

    @abstractmethod
    def set_teardown_checker(self, checker: checker.Checker):
        pass

    def set_surface(self, surface: surface.Surface):
        pass

    @abstractmethod
    def get_result(self):
        pass


class VectorPictureBuilder(Builder):
    def __init__(self, height, width):
        self.picture = VectorPicture()
        self.picture.height = height
        self.picture.width = width

    def reset(self):
        self.picture = VectorPicture()

    def set_start_positions_matrix(self, grid: grid.Grid):
        self.picture.start_positions_matrix = grid.matrix

    def set_angle_matrix(self, distortion: distortion.Distortion):
        self.picture.angle_matrix = distortion.matrix

    def set_checker(self, checker: checker.Checker):
        self.picture.checkers.append(checker)

    def set_teardown_checker(self, checker: checker.Checker):
        self.picture.teardown_checkers.append(checker)

    def set_steps_params(self, steps_counts: int, steps_length: int):
        self.picture.steps_count = steps_counts
        self.picture.steps_length = steps_length

    def set_surface(self, surface: surface.Surface):
        self.picture.surface = surface

    def get_result(self):
        return self.picture


def main():
    height, width = 256, 256
    builder = VectorPictureBuilder(height, width)
    builder.set_surface(
        surface.SVGSurfaceBuilder(height, width)
            .set_lines_stroke('black', 1)
            .set_lines_fill('none')
            .get_instance(),
    )

    builder.set_start_positions_matrix(
        grid.RandomGridBuilder(height, width, 256*4).get_instance()
    )
    builder.set_angle_matrix(
        distortion.PerlinNoiseDistortionBuilder(height, width)
            # .set_angle_step(0.25*np.pi)
            # .set_noise_type(fns.NoiseType.WhiteNoise)
            .set_frequency(0.001).get_instance(),
    )

    builder.set_steps_params(1000, 1)

    builder.set_checker(
        checker.DistanceChecker(radius=3)
    )
    builder.set_teardown_checker(
        checker.LineLengthChecker(10)
    )
    picture = builder.get_result()
    picture.draw()
    picture.save('one.svg')
    os.system('chromium one.svg')


if __name__ == '__main__':
    main()
