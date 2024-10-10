import os

VECTOR_MODEL_VAR = os.environ.get('VECTOR_MODEL')

# Print the variable value
print(f"DEBUG(init-app.py): env VECTOR_MODEL-{VECTOR_MODEL_VAR}")
