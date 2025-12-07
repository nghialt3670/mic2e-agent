from typing import List

from app.core.chat2edit.models.fabric.objects import FabricObject


def get_own_objects(objects: List[FabricObject]) -> List[FabricObject]:
    object_ids = set(map(lambda obj: obj.id, objects))
    return list(filter(lambda obj: obj.id in object_ids, objects))
