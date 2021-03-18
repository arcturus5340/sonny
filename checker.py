from abc import ABC, abstractmethod
import numpy as np
import typing

from sklearn.neighbors import KDTree


class Checker(ABC):
    @abstractmethod
    def load(self, *args, **kwargs):
        pass

    @abstractmethod
    def result(self):
        pass


class TearDownChecker(Checker):
    @abstractmethod
    def load(self, *args, **kwargs):
        pass

    @abstractmethod
    def result(self):
        pass


class DistanceChecker(Checker):
    def __init__(self, radius):
        self.radius = radius
        self.x: typing.Optional[int] = None
        self.y: typing.Optional[int] = None
        self.all_points: typing.Optional[np.ndarray] = None

    def load(self, *args, **kwargs):
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')
        self.all_points = kwargs.get('all_points')
        assert self.x is not None and self.y is not None and self.all_points is not None

    def result(self):
        points_tree = KDTree(self.all_points)
        all_nn_indices = points_tree.query_radius([(self.x, self.y)], r=self.radius)
        return all_nn_indices[0].size == 0


class LineLengthChecker(TearDownChecker):
    def __init__(self, line_len: int):
        self.line_len: int = line_len
        self.actual_len: typing.Optional[int] = None

    def load(self, *args, **kwargs):
        self.actual_len = kwargs.get('length')
        assert self.actual_len is not None

    def result(self):
        return self.actual_len > self.line_len
