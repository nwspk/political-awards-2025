import csv
from datetime import datetime

def process_data(header, rows):
    # Verify required columns exist
    required_columns = {'website', 'last_update'}
    if not required_columns.issubset(header):
        missing = required_columns - set(header)
        raise ValueError(f"Missing required columns: {missing}")

    # Get indices of required columns
    website_idx = header.index('website')
    last_update_idx = header.index('last_update')

    # Select only the required columns
    selected_data = [
        [row[website_idx], row[last_update_idx]]
        for row in rows
    ]

    # Filter out rows with last_update = 'N/A'
    filtered_data = [
        row for row in selected_data
        if row[1] != 'N/A'
    ]

    # Validate timestamp format and convert to datetime objects
    timestamps = []
    for row in filtered_data:
        try:
            dt = datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%SZ')
            timestamps.append(dt)
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {row[1]}. Expected format: YYYY-MM-DDTHH:MM:SSZ")

    # Calculate time differences (weights for award distribution)
    now = datetime.utcnow()
    time_diffs = [(now - dt).total_seconds() for dt in timestamps]

    # Avoid division by zero if all timestamps are the same
    if all(diff == 0 for diff in time_diffs):
        weights = [1] * len(time_diffs)
    else:
        # More recent timestamps get higher weights
        weights = [1 / (diff + 1) for diff in time_diffs]

    # Normalize weights to sum to 1
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # Calculate awards (sum to 3,000,000)
    total_award = 3_000_000
    awards = [int(round(w * total_award)) for w in normalized_weights]

    # Adjust awards to ensure they sum exactly to 3,000,000
    award_sum = sum(awards)
    difference = total_award - award_sum
    if difference != 0:
        awards[0] += difference  # Add the difference to the first award

    # Add awards to the data
    result_header = ['website', 'last_update', 'award']
    result_rows = [
        [filtered_data[i][0], filtered_data[i][1], str(awards[i])]
        for i in range(len(filtered_data))
    ]

    return result_header, result_rows
