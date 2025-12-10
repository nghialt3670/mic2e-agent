from chat2edit.models import Feedback
from chat2edit.utils import SmartTypeAdapter

class CustomFeedback(Feedback):
    type: str = "custom"
    severity: str = "error"
    message: str
    custom_field: str

feedback = CustomFeedback(severity="error", message="This is a custom feedback", custom_field="This is a custom field")
json_feedback = feedback.model_dump_json()

adapter = SmartTypeAdapter(Feedback)
adapted_feedback = adapter.validate_json(json_feedback)

print(type(adapted_feedback))