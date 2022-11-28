from learning_environment.its.tutor.base import BaseTutorModel
from learning_environment.its.tutor.smart import SmartTutorModel
from learning_environment.models import User


def get_tutor_model(tutor_mode: str, user: User) -> BaseTutorModel:
    tutor = BaseTutorModel(user)

    if tutor_mode == "S":
        tutor = SmartTutorModel(user)

    return tutor
