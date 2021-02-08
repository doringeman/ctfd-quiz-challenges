from flask import Blueprint

from CTFd.models import Challenges, Fails, Solves, db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.utils.user import get_ip

__version__ = "0.1-dev"

class QuizChallengeModel(Challenges):
    __mapper_args__ = {"polymorphic_identity": "quiz"}

    id = db.Column(
        db.Integer,
        db.ForeignKey("challenges.id", ondelete="CASCADE"),
        primary_key=True
    )

    variant_a = db.Column(db.String(100), default="")
    variant_b = db.Column(db.String(100), default="")
    variant_c = db.Column(db.String(100), default="")
    variant_d = db.Column(db.String(100), default="")

    correct_variant = db.Column(db.String(1), default="A")

    def __init__(self, *args, **kwargs):
        super(QuizChallengeModel, self).__init__(**kwargs)

class QuizChallenge(BaseChallenge):
    id = "quiz"
    name = "quiz"
    templates = {
        "create": "/plugins/quiz_challenges/assets/create.html",
        "update": "/plugins/quiz_challenges/assets/update.html",
        "view": "/plugins/quiz_challenges/assets/view.html",
    }
    scripts = {
        "create": "/plugins/quiz_challenges/assets/create.js",
        "update": "/plugins/quiz_challenges/assets/update.js",
        "view": "/plugins/quiz_challenges/assets/view.js",
    }
    route = "/plugins/quiz_challenges/assets/"
    blueprint = Blueprint(
        "quiz_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = QuizChallengeModel

    @classmethod
    def read(cls, challenge):
        challenge = QuizChallengeModel.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "description": challenge.description,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },

            "variant_a": challenge.variant_a,
            "variant_b": challenge.variant_b,
            "variant_c": challenge.variant_c,
            "variant_d": challenge.variant_d,
            "correct_variant": challenge.correct_variant,
        }
        return data

    @classmethod
    def attempt(cls, challenge, request):
        data = request.form or request.get_json()
        try:
            variant = next(filter(lambda x: data[x] is True, filter(lambda x: x.startswith("variant"), data.keys())))
            print(challenge.correct_variant, variant[-1].upper())
            correct = (challenge.correct_variant == variant[-1].upper())
        except:
            correct = False
        return correct, "Correct" if correct else "Incorrect"

    @classmethod
    def solve(cls, user, team, challenge, request):
        data = request.form or request.get_json()
        provided = ",".join(
            map(
                lambda x: x.split("_")[-1].upper(),
                filter(lambda x: data[x] is True, data)
            )
        )
        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=provided,
        )
        db.session.add(solve)
        db.session.commit()

    @classmethod
    def fail(cls, user, team, challenge, request):
        data = request.form or request.get_json()
        provided = ",".join(
            map(
                lambda x: x.split("_")[-1].upper(),
                filter(lambda x: data[x] is True, data)
            )
        )
        fail = Fails(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(request),
            provided=provided,
        )
        db.session.add(fail)
        db.session.commit()

def load(app):
    app.db.create_all()
    CHALLENGE_CLASSES["quiz"] = QuizChallenge
    register_plugin_assets_directory(
        app,
        base_path="/plugins/quiz_challenges/assets/"
    )
