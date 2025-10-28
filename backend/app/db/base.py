from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models for metadata
from app.models.rulepack import RulePack, Rule  # noqa: F401,E402
from app.models.dataset import Dataset  # noqa: F401,E402
from app.models.run import Run, RunRuleResult, DecisionTrace  # noqa: F401,E402
