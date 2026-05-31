from chat2edit.models import (
    Exemplar,
    ExemplaryChatCycle,
    ExemplaryExecutionBlock,
    ExemplaryPromptCycle,
    ExemplaryPromptExchange,
    Feedback,
    Message,
)


def create_interactive_exemplars() -> list[Exemplar]:
    """Create exemplars for interactive mode (with point, box, scribble support)."""
    return [
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


def create_non_interactive_exemplars() -> list[Exemplar]:
    """Create exemplars for non-interactive mode (text-based prompts only, no point/box/scribble)."""
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
dog_list_0 = segment_objects(image_0, prompt='dog', expected_quantity=1)
```
""".strip(),
                                    ),
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
dog_list_0 = segment_objects(image_0, prompt='dog', expected_quantity=1)
""".strip(),
                                    feedback=Feedback(
                                        type="prompt_based_object_detection_quantity_mismatch",
                                        severity="error",
                                        function="segment_objects",
                                        attachments=["annotated_image_0"],
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
thinking: The segment_objects function couldn't find any dogs in the image. I should inform the user about this and show them the annotated image. Since I cannot use interactive annotations, I should ask them to provide a more specific description or try a different approach.
commands:
```python
respond_user(text='I could not find any dogs in the image. Please check the annotated image and provide a more specific description, or try rephrasing your request.', attachments=[annotated_image_0])
```
""".strip(),
                                    ),
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='I could not find any dogs in the image. Please check the annotated image and provide a more specific description, or try rephrasing your request.', attachments=[annotated_image_0])
""".strip(),
                                    response=Message(
                                        text="I could not find any dogs in the image. Please check the annotated image and provide a more specific description, or try rephrasing your request.",
                                        attachments=["annotated_image_0"],
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
                        text="Add the dog from the first image to the left of the cat in the second image",
                        attachments=["image_0", "image_1"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: The user wants to add an object from the first image to the left of an object in the second image. I need to segment the dog from the first image, segment the cat from the second image, then paste the dog to the left of the cat using paste_entities with anchor.
commands:
```python
dog_list_0 = segment_objects(image_0, prompt='dog', expected_quantity=1)
cat_list_0 = segment_objects(image_1, prompt='cat', expected_quantity=1)
image_2 = paste_entities(image_1, entities=[dog_list_0[0]], positions=['left'], anchor=cat_list_0[0])
respond_user(text='The dog has been added to the left of the cat', attachments=[image_2])
```
""".strip(),
                                    )
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
dog_list_0 = segment_objects(image_0, prompt='dog', expected_quantity=1)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
cat_list_0 = segment_objects(image_1, prompt='cat', expected_quantity=1)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
image_2 = paste_entities(image_1, entities=[dog_list_0[0]], positions=['left'], anchor=cat_list_0[0])
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='The dog has been added to the left of the cat', attachments=[image_2])
""".strip(),
                                    response=Message(
                                        text="The dog has been added to the left of the cat",
                                        attachments=["image_2"],
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
                        text="Remove all the cats from the image",
                        attachments=["image_0"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: I need to detect all cats in the image and remove them.
commands:
```python
cat_list_0 = segment_objects(image_0, prompt='cat', expected_quantity=2)
image_1 = remove_entities(image_0, cat_list_0)
respond_user(text='All cats have been removed from the image', attachments=[image_1])
```
""".strip(),
                                    )
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
cat_list_0 = segment_objects(image_0, prompt='cat', expected_quantity=2)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
image_1 = remove_entities(image_0, cat_list_0)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='All cats have been removed from the image', attachments=[image_1])
""".strip(),
                                    response=Message(
                                        text="All cats have been removed from the image",
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
                        text="Rotate the dog 90 degrees clockwise",
                        attachments=["image_0"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: I need to find the dog in the image first, then rotate it.
commands:
```python
dog_list_0 = segment_objects(image_0, prompt='dog', expected_quantity=1)
image_1 = rotate_entities(image_0, entities=dog_list_0, angles=[90], units=['degree'], directions=['cw'])
respond_user(text='The dog has been rotated 90 degrees clockwise', attachments=[image_1])
```
""".strip(),
                                    )
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
dog_list_0 = segment_objects(image_0, prompt='dog', expected_quantity=1)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
image_1 = rotate_entities(image_0, entities=dog_list_0, angles=[90], units=['degree'], directions=['cw'])
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='The dog has been rotated 90 degrees clockwise', attachments=[image_1])
""".strip(),
                                    response=Message(
                                        text="The dog has been rotated 90 degrees clockwise",
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
                        text="Increase the brightness by 50%",
                        attachments=["image_0"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: The user wants to increase the brightness by 50%. I should apply a brightness filter with value 0.5.
commands:
```python
image_1 = apply_filter(image_0, filter_name='brightness', filter_value=0.5)
```
""".strip(),
                                    )
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
image_1 = apply_filter(image_0, filter_name='brightness', filter_value=0.5)
""".strip(),
                                    feedback=Feedback(
                                        type="filter_value_offset_from_optimal",
                                        severity="warning",
                                        function="apply_filter",
                                        details={
                                            "filter_name": "brightness",
                                            "filter_value": 0.5,
                                            "optimal_value": 0.0664,
                                            "optimal_score_percent": 6.64,
                                            "offset": 0.4336,
                                            "is_opposite_direction": False,
                                        },
                                        contextualized=True,
                                    ),
                                ),
                            ],
                        ),
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: The apply_filter function gave feedback that the brightness filter value (0.5, which is 50% increase as the user requested) is too far from the optimal aesthetic value (0.0664, 6.64% adjustment needed). The system suggests that 6.64% brightness increase would be more aesthetically pleasing. I should inform the user about this and ask if they want to proceed with the 6.64% (more aesthetic) or keep the 50% they requested.
commands:
```python
respond_user(text='I applied the 50% brightness increase as you requested. However, the system suggests that a 6.64% brightness increase would be more aesthetically pleasing. Would you like me to adjust it to 6.64% instead, or keep the 50% increase?', attachments=[image_1])
```
""".strip(),
                                    )
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='I applied the 50% brightness increase as you requested. However, the system suggests that a 6.64% brightness increase would be more aesthetically pleasing. Would you like me to adjust it to 6.64% instead, or keep the 50% increase?', attachments=[image_1])
""".strip(),
                                    response=Message(
                                        text="I applied the 50% brightness increase as you requested. However, the system suggests that a 6.64% brightness increase would be more aesthetically pleasing. Would you like me to adjust it to 6.64% instead, or keep the 50% increase?",
                                        attachments=["image_1"],
                                        contextualized=True,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                ExemplaryChatCycle(
                    request=Message(
                        text="Yes, let's try the 6.64% brightness increase",
                        attachments=["image_0"],
                        contextualized=True,
                    ),
                    cycles=[
                        ExemplaryPromptCycle(
                            exchanges=[
                                ExemplaryPromptExchange(
                                    answer=Message(
                                        text="""
thinking: The user wants to try the suggested 6.64% brightness increase. I should apply the brightness filter with value 0.0664 to the original image (image_0) to get the optimal aesthetic result.
commands:
```python
image_2 = apply_filter(image_0, filter_name='brightness', filter_value=0.0664)
respond_user(text='I have applied the suggested 6.64% brightness increase to the image. This provides a more aesthetically pleasing result.', attachments=[image_2])
```
""".strip(),
                                    )
                                ),
                            ],
                            blocks=[
                                ExemplaryExecutionBlock(
                                    generated_code="""
image_2 = apply_filter(image_0, filter_name='brightness', filter_value=0.0664)
""".strip(),
                                ),
                                ExemplaryExecutionBlock(
                                    generated_code="""
respond_user(text='I have applied the suggested 6.64% brightness increase to the image. This provides a more aesthetically pleasing result.', attachments=[image_2])
""".strip(),
                                    response=Message(
                                        text="I have applied the suggested 6.64% brightness increase to the image. This provides a more aesthetically pleasing result.",
                                        attachments=["image_2"],
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


def create_mic2e_exemplars(interactive: bool = True) -> list[Exemplar]:
    """Create exemplars based on interactive mode."""
    if interactive:
        return create_interactive_exemplars() + create_non_interactive_exemplars()
    else:
        return create_non_interactive_exemplars()


# Default exemplars for backward compatibility (interactive mode)
MIC2E_EXEMPLARS = create_mic2e_exemplars(interactive=True)
