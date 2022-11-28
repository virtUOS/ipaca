from learning_environment.its.tutor.base import BaseTutorModel
from learning_environment.models import User


def get_tutor_model(tutor_mode: str, user: User) -> BaseTutorModel:
    tutor = BaseTutorModel(user)

    return tutor
