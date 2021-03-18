from abc import ABC, abstractmethod
import math
import numpy as np
import time
import typing

import pyfastnoisesimd as fns


class Distortion:
    def __init__(self):
        self.matrix: typing.Optional[np.ndarray] = None


class DistortionBuilder(ABC):
    @abstractmethod
    def get_instance(self):
        pass


class PerlinNoiseDistortionBuilder(DistortionBuilder):
    def __init__(self, height, width, seed=None):
        self.distortion = Distortion()
        self.height = height
        self.width = width
        if not seed:
            seed = time.time_ns()
        self.perlin_noise = fns.Noise(seed)
        self.normalizing_lambda = lambda x: x*2*np.pi

    def set_frequency(self, frequency: float):
        self.perlin_noise.frequency = frequency
        return self

    def set_noise_type(self, noise_type: fns.NoiseType):
        self.perlin_noise.noiseType = noise_type
        return self

    def set_angle_step(self, step):
        self.normalizing_lambda = lambda x: math.ceil(x*2*np.pi/step)*step
        return self

    def get_instance(self):
        perlin_noise_matrix = self.perlin_noise.genAsGrid(shape=[self.height, self.width], start=[0, 0])
        self.distortion.matrix = np.vectorize(self.normalizing_lambda)(perlin_noise_matrix)
        return self.distortion
