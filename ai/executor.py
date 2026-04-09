def run_model(mode, user_input, history=None):

    try:
        from ai.executor_core import run_model_core
        return run_model_core(mode, user_input, history=history)

    except Exception as e:
        return f"""
================ AI SYSTEM ================

MODE:
❌ ERROR

------------------------------------------

{str(e)}

==========================================
"""
