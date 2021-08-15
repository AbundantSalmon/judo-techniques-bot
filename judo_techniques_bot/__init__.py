import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
print("Added to PYTHONPATH:")
print(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
