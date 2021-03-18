from abc import ABC, abstractmethod
import drawSvg
import typing


class Surface(ABC):
    class Line(ABC):
        def start_point(self, x, y):
            pass

        def next_point(self, x, y):
            pass

    @abstractmethod
    def draw(self, line: Line):
        pass

    @abstractmethod
    def save(self, path):
        pass


class SurfaceBuilder(ABC):
    @abstractmethod
    def get_instance(self):
        pass


class SVGSurface(Surface):
    def __init__(self, height, width):
        self.surface = drawSvg.Drawing(width, height)
        self.line: typing.Optional[Surface.Line] = None

    class Line(Surface.Line):
        def __init__(self, stroke: str = 'black', stroke_width: str = 1, fill: str = 'none'):
            self.stroke = stroke
            self.stroke_width = stroke_width
            self.fill = fill

        def start_point(self, x, y):
            self.path = drawSvg.Path(
                stroke=self.stroke,
                stroke_width=self.stroke_width,
                fill=self.fill
            )
            self.path.M(x, y)

        def next_point(self, x, y):
            self.path.L(x, y)

    def draw(self, line: Line):
        self.surface.append(line.path)

    def save(self, path):
        self.surface.saveSvg(path)


class SVGSurfaceBuilder(SurfaceBuilder):
    def __init__(self, width, height):
        self.surface = SVGSurface(width, height)
        self.surface.line = self.surface.Line()
        self.line_params = dict()

    def set_lines_stroke(self, stroke, stroke_width):
        self.line_params['stroke'] = stroke
        self.line_params['stroke_width'] = stroke_width
        return self

    def set_lines_fill(self, fill):
        self.line_params['fill'] = fill
        return self

    def get_instance(self):
        self.surface.line = self.surface.Line(**self.line_params)
        return self.surface
