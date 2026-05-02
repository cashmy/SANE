from app.models.enums import DecisionValue, ExternalActionStatus


def build_external_action_status(_: DecisionValue) -> ExternalActionStatus:
    return ExternalActionStatus.not_executed


def execute_external_action(_: DecisionValue) -> None:
    raise RuntimeError("External email actions are outside the Stage 1 ALPHA boundary.")
