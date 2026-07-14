import pathlib
import sys

# Put backend/ on sys.path so `from database.models import ...` resolves under pytest.
sys.path.insert(0, str(pathlib.Path(__file__).parent))
