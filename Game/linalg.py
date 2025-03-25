import math

class Vector:
    def __init__(self, x: float, y: float = None, coordinates_plane: str = "cartesian") -> None:
        if coordinates_plane == "cartesian":
            if y == None:
                self.x: float = x[0]
                self.y: float = x[1]
            else:
                self.x = x
                self.y = y

        elif coordinates_plane == "polar":
            if y == None:
                self.x = x[0] * math.cos(x[1])
                self.y = x[0] * math.sin(x[1])
            else:
                self.x = x * math.cos(y)
                self.y = x * math.sin(y)

    def __str__(self) -> str:
        return f"[{self.x:.2f}\n {self.y:.2f}]"

    def __add__(self, other) -> "Vector":
        if not isinstance(other, Vector):
            if isinstance(other, tuple) or isinstance(other, list):
                return Vector(self.x + other[0], self.y + other[1])
            raise TypeError(f"Soma inválida")
        
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> "Vector":
        if not isinstance(other, Vector):
            if isinstance(other, tuple) or isinstance(other, list):
                return Vector(self.x - other[0], self.y - other[1])
            raise TypeError(f"Subtração inválida")
        
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other) -> "Vector":
        if not (isinstance(other, float) or isinstance(other, int)):
            raise TypeError(f"Multiplicação só pode ocorrer com números.")

        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other) -> "Vector":
        if not (isinstance(other, float) or isinstance(other, int)):
            raise TypeError(f"Divisão só pode ocorrer com números.")

        return Vector(self.x / other, self.y / other)
    
    def __neg__(self) -> "Vector":
        return Vector(-self.x, -self.y)
    
    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        return self.y

    def dot(self, other) -> "Vector":
        if not isinstance(other, Vector):
            if isinstance(other, tuple) or isinstance(other, list):
                return self.x * other[0] + self.y * other[1]
            raise TypeError(f"Produto escalar inválido")
        
        return self.x * other.x + self.y * other.y

    def cross_2D(self, other) -> "Vector":
        if not isinstance(other, Vector):
            if isinstance(other, tuple) or isinstance(other, list):
                return self.x * other[1] -  self.y * other[0]
            raise TypeError(f"Produto cruzado inválido")
        
        return self.x * other.y - self.y * other.x
    
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def magnitude_squared(self) -> float:
        return self.x ** 2 + self.y ** 2
    
    def normal(self, other) -> "Vector":
        perpendicular: Vector = self.perpendicular(other)
        difference: Vector = other - self
        magnitude: float = difference.magnitude()
        return perpendicular / magnitude

    def perpendicular(self, other) -> "Vector":
        difference: Vector = other - self
        return Vector(-difference.y, difference.x)

    def normalize(self) -> None:
        magnitude: float = self.magnitude()
        x = self.x / magnitude
        y = self.y / magnitude
        return Vector(x, y)

    def distance(self, other) -> "Vector":
        difference: Vector = other - self
        return difference.magnitude()

    def to_list(self) -> list:
        return [self.x, self.y]

    def to_tuple(self) -> tuple:
        return (self.x, self.y)
    
    def angle(self, other) -> float:
        center_vector: Vector = self - other
        magnitude: float = center_vector.magnitude()
        identity_vector: Vector = Vector(1, 0)

        if magnitude == 0:
            return 0

        if other.y > self.y:
            return math.acos(center_vector.dot(identity_vector) / magnitude)

        return 2 * math.pi - math.acos(center_vector.dot(identity_vector) / magnitude)
    
class Matrix:
    def __init__(self, matrix: list) -> None:
        if isinstance(matrix[0], Vector):
            self.matrix = matrix
        else:
            self.matrix = [Vector(matrix[i][0], matrix[i][1]) for i in range(len(matrix))]

        self.length = len(matrix)

    def __str__(self) -> str:
        first_column: str = "["
        second_column: str = ""
        for vector in self.matrix:
            first_column = first_column + f"{vector.x:.2f} "
            second_column = second_column + f"{vector.y:.2f} "

        first_column = first_column[:-1] + ""
        second_column = second_column[:-1] + "]"
        return f"{first_column}\n {second_column}"

    def __getitem__(self, index: int) -> Vector:
        return self.matrix[index]

    def __len__(self):
        return len(self.matrix)
    
    def set_matrix(self, matrix: list) -> None:
        if isinstance(matrix[0], Vector):
            self.matrix = matrix
        else:
            self.matrix = [Vector(matrix[i][0], matrix[i][1]) for i in range(len(matrix))]

        self.length = len(matrix)

    def rigid_transform(self, pos: Vector, angle: float) -> None:
        matrix: list = [Vector(
            pos[0] + math.cos(math.radians(angle)) * self.matrix[i].x + math.sin(math.radians(angle)) * self.matrix[i].y,
            pos[1] - math.sin(math.radians(angle)) * self.matrix[i].x + math.cos(math.radians(angle)) * self.matrix[i].y
            ) for i in range(self.length)]

        return Matrix(matrix)