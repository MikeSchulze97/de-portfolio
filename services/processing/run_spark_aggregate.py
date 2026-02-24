import runpy

if __name__ == "__main__":
    # Execute run_aggregate.py as if it was called via `python run_aggregate.py ...`
    runpy.run_module("run_aggregate", run_name="__main__")