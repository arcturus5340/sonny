from abc import ABC, abstractmethod
import numpy as np
import typing


class Grid:
    def __init__(self):
        self.matrix: typing.Optional[np.ndarray] = None


class GridBuilder(ABC):
    @abstractmethod
    def get_instance(self):
        pass


class RandomGridBuilder(GridBuilder):
    def __init__(self, height, width, count):
        self.grid = Grid()
        self.height = height
        self.width = width
        self.count = count

    def get_instance(self):
        y_axis = np.random.randint(self.height, size=self.count).reshape((self.count, 1))
        x_axis = np.random.randint(self.width, size=self.count).reshape((self.count, 1))
        self.grid.matrix = np.concatenate((x_axis, y_axis), axis=1)
        return self.grid


class RegularGridBuilder(GridBuilder):
    def __init__(self, height, width, step):
        self.grid = Grid()
        self.height = height
        self.width = width
        self.step = step

    def get_instance(self):
        arrays = range(0, self.height, self.step), range(0, self.width, self.step)
        arr = np.empty([len(a) for a in arrays] + [2], dtype=np.int32)
        for i, a in enumerate(np.ix_(*arrays)):
            arr[..., i] = a
        self.grid.matrix = arr.reshape(-1, 2)
        return self.grid


class BorderGridBuilder(GridBuilder):
    def __init__(self, height, width, step):
        self.grid = Grid()
        self.height = height
        self.width = width
        self.step = step

    def get_instance(self):
        x_axis = np.arange(0, self.width, self.step).reshape((self.width // self.step, 1))
        y_axis = np.arange(0, self.height, self.step).reshape((self.width // self.step, 1))
        matrix = np.concatenate((x_axis, np.full_like(x_axis, 0)), axis=1)
        matrix = np.concatenate((np.concatenate((np.full_like(y_axis, 0), y_axis), axis=1), matrix))
        matrix = np.concatenate((np.concatenate((np.full_like(x_axis, self.width-1), y_axis), axis=1), matrix))
        matrix = np.concatenate((np.concatenate((x_axis, np.full_like(y_axis, self.height-1)), axis=1), matrix))
        self.grid.matrix = matrix
        return self.grid
