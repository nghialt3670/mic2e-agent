from chat2edit.models import (
    Exemplar,
    ExemplaryChatCycle,
    ExemplaryExecutionBlock,
    ExemplaryPromptCycle,
    ExemplaryPromptExchange,
    Feedback,
    Message,
)


def create_mic2e_exemplars() -> list[Exemplar]:
    return [
        Exemplar(
            cycles=[
                ExemplaryChatCycle(
                    request=Message(
                        text="Remove the dog from the image",
                        attachments=["image_0"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking:I need to detect the dog before I can remove it from the image
commands:
```python
dogs_0 = detect_objects(image_0, prompt='dog', expected_quantity=1)
```
""".strip(),
                                    ),
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
dogs_0 = detect_objects(image_0, prompt='dog', expected_quantity=1)
""".strip(),
                                    feedback=Feedback(
                                        type="prompt_based_object_detection_quantity_mismatch",
                                        severity="error",
                                        function="detect_objects",
                                        details={
                                            "prompt": "dog",
                                            "expected_quantity": 1,
                                            "detected_quantity": 0,
                                        },
                                        contextualized=True,
                                    ),
                                )
                            ],
                        ),
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: The detect_objects function couldn't find any dogs in the image. Since there is the segment_object function, I could try ask the user for the bounding box of the dog in the image and use the segment_object function to extract the dog from the image
commands:
```python
respond_user(text='I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?')
```
""".strip(),
                                    ),
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?')
""".strip(),
                                    response=Message(
                                        text="I can't find any dogs in the image. Can you please provide me the bounding box of the dog in the image?",
                                        attachments=["image_0"],
                                        contextualized=True,
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            ]
        ),
        Exemplar(
            cycles=[
                ExemplaryChatCycle(
                    request=Message(
                        text="Remove the cat in @box_0 and the bird in @box_1 from the image",
                        attachments=["image_0", "box_0", "box_1"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: since the user provided the bounding boxes of the cat and the bird, I need to segment them from the image and then remove them.
commands:
```python
cat_0 = segment_object(image_0, box=box_0)
bird_0 = segment_object(image_0, box=box_1)
image_1 = remove_entities(image_0, [cat_0, bird_0])
respond_user(text='The cat and the bird have been removed from the image', attachments=[image_1])
```
""".strip(),
                                    ),
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
cat_0 = segment_object(image_0, box=box_0)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
bird_0 = segment_object(image_0, box=box_1)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
image_1 = remove_entities(image_0, [cat_0, bird_0])
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='The cat and the bird have been removed from the image', attachments=[image_1])
""".strip(),
                                    response=Message(
                                        text="The cat and the bird have been removed from the image",
                                        attachments=["image_1"],
                                        contextualized=True,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        ),
        Exemplar(
            cycles=[
                ExemplaryChatCycle(
                    request=Message(
                        text="Rotate @point_0",
                        attachments=["image_0", "point_0"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: The user wants to rotate the object at the point. I need to first extract the object using the point, then rotate it.
commands:
```python
obj_0 = segment_object(image_0, positive_points=[point_0])
image_1 = rotate_entities(image_0, entities=[obj_0], angles=[90])
respond_user(text='The object has been rotated', attachments=[image_1])
```
""".strip(),
                                    )
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
obj_0 = segment_object(image_0, positive_points=[point_0])
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
image_1 = rotate_entities(image_0, entities=[obj_0], angles=[90])
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='The object has been rotated', attachments=[image_1])
""".strip(),
                                    response=Message(
                                        text="The object has been rotated",
                                        attachments=["image_1"],
                                        contextualized=True,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        ),
    ]


MIC2E_EXEMPLARS = create_mic2e_exemplars()
