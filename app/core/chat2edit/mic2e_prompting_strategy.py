from chat2edit.models import Feedback
from chat2edit.prompting.strategies import OtcPromptingStrategy

PROMPT_BASED_OBJECT_DETECTION_QUANTITY_MISMATCH_FEEDBACK_TEXT = "Expected to extract {expected_quantity} object(s) with prompt '{prompt}', but found {detected_quantity} object(s)."
MISSING_FILTER_VALUE_FEEDBACK_TEXT = (
    "Filter value is required for filter '{filter_name}'."
)
INVALID_FILTER_VALUE_FEEDBACK_TEXT = "Filter value '{filter_value}' is invalid for filter '{filter_name}'. It must be between -1.0 and 1.0."
FILTER_VALUE_OFFSET_FROM_OPTIMAL_FEEDBACK_TEXT = (
    "The {filter_name} filter value ({filter_value}) is {offset_percent:.1f}% away from the optimal value ({optimal_value}, {optimal_score_percent:.1f}% adjustment needed)."
    "{direction_warning}"
)


class Mic2ePromptingStrategy(OtcPromptingStrategy):
    def __init__(self) -> None:
        super().__init__()

    def create_feedback_text(self, feedback: Feedback) -> str:
        feedback_type = feedback.type
        details = feedback.details

        if feedback_type == "missing_filter_value":
            return MISSING_FILTER_VALUE_FEEDBACK_TEXT.format(
                filter_name=details.get("filter_name"),
            )

        if feedback_type == "invalid_filter_value":
            return INVALID_FILTER_VALUE_FEEDBACK_TEXT.format(
                filter_name=details.get("filter_name"),
                filter_value=str(details.get("filter_value")),
            )

        if feedback_type == "prompt_based_object_detection_quantity_mismatch":
            return PROMPT_BASED_OBJECT_DETECTION_QUANTITY_MISMATCH_FEEDBACK_TEXT.format(
                prompt=details.get("prompt"),
                expected_quantity=details.get("expected_quantity"),
                detected_quantity=details.get("detected_quantity"),
            )

        if feedback_type == "filter_value_offset_from_optimal":
            filter_name = details.get("filter_name", "filter")
            filter_value = details.get("filter_value", 0.0)
            optimal_value = details.get("optimal_value", 0.0)
            optimal_score_percent = details.get("optimal_score_percent", 0.0)
            offset = details.get("offset", 0.0)
            is_opposite_direction = details.get("is_opposite_direction", False)

            offset_percent = offset * 100.0

            direction_warning = ""
            if is_opposite_direction:
                direction_warning = " This adjustment goes in the opposite direction of what the image needs."

            return FILTER_VALUE_OFFSET_FROM_OPTIMAL_FEEDBACK_TEXT.format(
                filter_name=filter_name,
                filter_value=filter_value,
                optimal_value=optimal_value,
                optimal_score_percent=optimal_score_percent,
                offset_percent=offset_percent,
                direction_warning=direction_warning,
            )

        return super().create_feedback_text(feedback)
