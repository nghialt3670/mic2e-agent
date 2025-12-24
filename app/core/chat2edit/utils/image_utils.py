from typing import List
from app.core.chat2edit.models import Image
from app.core.chat2edit.models.fabric.objects import FabricObject


def get_own_objects(image: Image, objects: List[FabricObject]) -> List[FabricObject]:
    object_ids = set(obj.id for obj in objects)
    return [obj for obj in image.get_objects() if obj.id in object_ids]


def get_same_objects(image: Image, objects: List[FabricObject]) -> List[FabricObject]:
    coord_label_set = set(map(_get_coord_label, objects))
    same_objects = [
        obj for obj in image.get_objects()
        if _get_coord_label(obj) in coord_label_set
    ]

    return same_objects


def _get_coord_label(obj: FabricObject) -> str:
    return f"{obj.left}-{obj.top}-{obj.width}-{obj.height}"