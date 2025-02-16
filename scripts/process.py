import csv
import glob
import importlib.util
import os
import sys
from datetime import datetime

## This is an initial dummy script which assigns award based solely on how recent the 'last_update' field from the
## data csv is. Those without a last_update time get no award!

def load_algorithm():
    # Find all algorithm scripts
    algorithm_files = glob.glob("scripts/algorithm_*.py")

    if not algorithm_files:
        raise ValueError("No algorithm scripts found in scripts/ directory")

    # Get the newest algorithm file by modification time
    latest_script = max(algorithm_files, key=os.path.getmtime)
    script_name = os.path.basename(latest_script)[:-3]  # Remove .py extension

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location(script_name, latest_script)
    algorithm_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(algorithm_module)

    if not hasattr(algorithm_module, 'process_data'):
        raise AttributeError(f"Algorithm script {latest_script} has no 'process_data' function")

    return algorithm_module.process_data, script_name

def main():
    commit_hash = sys.argv[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Load algorithm and get version
    process_func, algorithm_version = load_algorithm()

    # Create results directory
    os.makedirs("results", exist_ok=True)

    # Read input data
    with open('data/grantmaking_projects_with_scraped_data.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Process data using the loaded algorithm
    processed_header, processed_rows = process_func(header, rows)

    # Generate output filename
    output_file = f"results/{timestamp}_{commit_hash}_{algorithm_version}.csv"

    # Write output
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(processed_header)
        writer.writerows(processed_rows)

    print(f"Generated {output_file} using {algorithm_version}")

if __name__ == "__main__":
    main()

