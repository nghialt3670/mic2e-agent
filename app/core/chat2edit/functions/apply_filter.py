from typing import List, Literal, Optional, Union

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_empty_list_parameters,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.execution.exceptions import FeedbackException
from chat2edit.execution.signaling import set_feedback
from chat2edit.models import Feedback
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.clients.inference_client import inference_client
from app.core.chat2edit.models import Image, Object
from app.core.chat2edit.models.fabric.filters import (
    BlackWhiteFilter,
    BlurFilter,
    BrightnessFilter,
    ContrastFilter,
    InvertFilter,
    SaturationFilter,
)
from app.core.chat2edit.utils import get_own_objects


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["entities"])
@exclude_coroutine
async def apply_filter(
    image: Image,
    filter_name: Literal[
        "blackWhite", "blur", "brightness", "contrast", "invert", "saturation"
    ],
    filter_value: Optional[float] = None,
    entities: Optional[List[Union[Image, Object]]] = None,
) -> Image:
    filter_obj = None

    if filter_value is not None:
        if filter_value < -1.0 or filter_value > 1.0:
            raise FeedbackException(
                Feedback(
                    type="invalid_filter_value",
                    severity="error",
                    details={"filter_name": filter_name, "filter_value": filter_value},
                )
            )

    if filter_name == "blackWhite":
        filter_obj = BlackWhiteFilter()
    elif filter_name == "blur":
        if filter_value is None:
            raise FeedbackException(
                Feedback(
                    type="missing_filter_value",
                    severity="error",
                    details={"filter_name": filter_name},
                )
            )
        filter_obj = BlurFilter(blur=filter_value)
    elif filter_name == "brightness":
        if filter_value is None:
            raise FeedbackException(
                Feedback(
                    type="missing_filter_value",
                    severity="error",
                    details={"filter_name": filter_name},
                )
            )
        filter_obj = BrightnessFilter(brightness=filter_value)
    elif filter_name == "contrast":
        if filter_value is None:
            raise FeedbackException(
                Feedback(
                    type="missing_filter_value",
                    severity="error",
                    details={"filter_name": filter_name},
                )
            )
        filter_obj = ContrastFilter(contrast=filter_value)
    elif filter_name == "invert":
        filter_obj = InvertFilter()
    elif filter_name == "saturation":
        if filter_value is None:
            raise FeedbackException(
                Feedback(
                    type="missing_filter_value",
                    severity="error",
                    details={"filter_name": filter_name},
                )
            )
        filter_obj = SaturationFilter(saturation=filter_value)

    # Check aesthetic scores for feedback (only for filters with values)
    # Only check if feedback hasn't been given yet for this image to avoid infinite feedback
    if (filter_value is not None 
        and filter_name in ["brightness", "saturation", "contrast"]
        and not image.aesthetic_feedback_given):
        try:
            # Get image BEFORE applying the new filter (current state)
            # We need to temporarily remove the filter we're about to apply
            # But actually, we should check BEFORE applying, so get current image state
            pil_image = image.get_image()
            scores = await inference_client.aesthetic_regressor_score(pil_image)
            
            # Map filter names to aesthetic score keys
            filter_to_score_key = {
                "brightness": "brightness",
                "saturation": "saturation",
                "contrast": "contrast",
            }
            
            score_key = filter_to_score_key[filter_name]
            optimal_score_percent = scores.get(score_key, 0.0)
            
            # Convert aesthetic score (percentage) to filter value (0-1 range)
            # Aesthetic score of 6.64 means +6.64%, which is filter_value = 0.0664
            optimal_filter_value = optimal_score_percent / 100.0
            
            # Calculate offset from optimal value
            offset = abs(filter_value - optimal_filter_value)
            
            # Check if filter value is too far from optimal, especially in opposite direction
            # Threshold: if offset > 0.1 (10%) or if going in opposite direction with offset > 0.05 (5%)
            is_opposite_direction = (optimal_filter_value > 0 and filter_value < 0) or (optimal_filter_value < 0 and filter_value > 0)
            threshold = 0.05 if is_opposite_direction else 0.1
            
            if offset > threshold:
                # Mark that feedback has been given for this image
                image.aesthetic_feedback_given = True
                set_feedback(
                    Feedback(
                        type="filter_value_offset_from_optimal",
                        severity="warning",
                        function="apply_filter",
                        details={
                            "filter_name": filter_name,
                            "filter_value": filter_value,
                            "optimal_value": optimal_filter_value,
                            "optimal_score_percent": optimal_score_percent,
                            "offset": offset,
                            "is_opposite_direction": is_opposite_direction,
                        },
                        contextualized=True,
                    )
                )
        except Exception as e:
            # Silently fail if aesthetic regressor is unavailable - don't block the filter operation
            pass

    if entities:
        own_objects = get_own_objects(image, entities)
        for obj in own_objects:
            if isinstance(obj, Image):
                obj.apply_filter(filter_obj)
            elif isinstance(obj, Object):
                obj.filters.append(filter_obj)
    else:
        image = image.apply_filter(filter_obj)

    return image
