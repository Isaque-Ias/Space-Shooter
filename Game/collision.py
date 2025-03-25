from linalg import *

class CollisionData:
    def __init__(self, overlap: float, mtv: float, vertex_a: int, vertex_b: int) -> None:
        self.main_object = True
        self.overlap = overlap
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.mtv = mtv

    def update_data(self, overlap: float, mtv: float, vertex_a: int, vertex_b: int) -> None:
        self.main_object = True
        self.overlap = overlap
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.mtv = mtv

    def set_relative_to_b(self) -> None:
        self.main_object = False
        self.mtv *= -1

class Collision:
    def __init__(self, first, second) -> None:
        self.main_body = first
        self.second_body = second
        self.data = None

    def __str__(self) -> str:
        return f"{self.main_body}\n{self.second_body}\nMTV = {self.data.mtv:.2f}\nOverlap = {self.data.overlap:.2f}\nIndices = {self.data.vertex_a} - {self.data.vertex_b}\nIsMain = {self.data.main_object}"

    def inform_data(self, data: CollisionData) -> None:
        self.data = data

def collision_with(handler, entity, group: str | bool = False, all_objects: bool = False) -> list | Collision | bool:
    collided: list = []

    if handler.object_groups.get(group):
        object_list: list = handler.object_groups[group]
    else:
        return False
    for group_element in object_list:
        if group_element.id == entity.id:
            continue
        
        collision: Collision | bool = test_collision(entity, group_element)

        if collision:
            if all_objects:
                collided.append(collision)
            else:
                return collision

    if collided and all_objects:
        return collided
    
    return False
    
def test_collision(first, second) -> Collision:
    collision = Collision(first, second)

    first_data: CollisionData = convex_sat(first, second)
    second_data: CollisionData = convex_sat(second, first)

    if first_data and second_data:
        if first_data.overlap > second_data.overlap:
            second_data.set_relative_to_b()
            final_data = second_data
        else:
            final_data = first_data

        collision.inform_data(final_data)
        return collision

    return False

def convex_sat(first, second) -> CollisionData:
    first_vertices: Matrix = first.display_vertices
    second_vertices: Matrix = second.display_vertices

    first_sides: int = first_vertices.length

    collision_data = CollisionData(float("inf"), 0, 0, 0)

    for first_vertex in enumerate(first_vertices):
        first_vertex_vector: Vector = first_vertex[1]
        next_index = (first_vertex[0] + 1) % first_sides
        next_vertex_vector: Vector = first_vertices[next_index]
        vertex_normal: Vector = first_vertex_vector.normal(next_vertex_vector)

        boundaries: list = {
            "a_min": float("inf"),
            "a_max": float("-inf"),
            "b_min": float("inf"),
            "b_max": float("-inf")
            }

        for first_vertex_sub in enumerate(first_vertices):
            first_vertex_sub_vector = first_vertex_sub[1]
            if first_vertex_sub[0] == first_vertex[0]:
                continue
            dot_value: float = vertex_normal.dot(first_vertex_sub_vector)

            if dot_value < boundaries["a_min"]:
                boundaries["a_min"] = dot_value

            if dot_value > boundaries["a_max"]:
                boundaries["a_max"] = dot_value

        for second_vertex_sub in enumerate(second_vertices):
            second_vertex_sub_vector = second_vertex_sub[1]
            dot_value: float = vertex_normal.dot(second_vertex_sub_vector)

            if dot_value < boundaries["b_min"]:
                boundaries["b_min"] = dot_value

            if dot_value > boundaries["b_max"]:
                boundaries["b_max"] = dot_value

        overlap: float = max(0, min(boundaries["a_max"], boundaries["b_max"]) - max(boundaries["a_min"], boundaries["b_min"]))
        mtv: float = 0
        if (boundaries["a_min"] + boundaries["a_max"]) > (boundaries["b_min"] + boundaries["b_max"]):
            mtv = boundaries["b_max"] - boundaries["a_min"]
        else:
            mtv = boundaries["b_min"] - boundaries["a_max"]

        #test mtv difference
        
        if overlap == 0:
            return False
        elif overlap < collision_data.overlap and mtv >= 0:
            collision_data.update_data(overlap, mtv, first_vertex[0], next_index)

    return collision_data########