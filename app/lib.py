def wow_analysis(wave_height_series, task_duration, wave_height_limit):
    """
    Analyze wave height series to identify suitable windows for task execution.

    Args:
        wave_height_series (list): List of wave height values
        task_duration (int): Required duration (number of consecutive data points)
        wave_height_limit (float): Maximum acceptable wave height

    Returns:
        tuple: (go_no_go_signals, start_indices)
            - go_no_go_signals: List of booleans indicating if conditions are met at each point
            - start_indices: List of indices where task can be started (beginning of valid windows)
    """
    n = len(wave_height_series)
    go_no_go_signals = []
    start_indices = []

    # Generate go/no-go signals for each data point
    for i in range(n):
        go_no_go_signals.append(wave_height_series[i] <= wave_height_limit)

    # Find valid start indices for task execution
    for i in range(n - task_duration + 1):
        # Check if the next task_duration points all satisfy the wave height limit
        valid_window = True
        for j in range(task_duration):
            if wave_height_series[i + j] > wave_height_limit:
                valid_window = False
                break

        if valid_window:
            start_indices.append(i)

    return go_no_go_signals, start_indices