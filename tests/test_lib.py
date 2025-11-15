from app.lib import wow_analysis


def test_wow_analysis_detects_valid_windows():
    wave_series = [1.5, 1.8, 1.7, 2.1, 1.9, 1.8, 1.2]
    task_duration = 3
    wave_limit = 2.0

    go_no_go, start_indices = wow_analysis(wave_series, task_duration, wave_limit)

    assert go_no_go == [True, True, True, False, True, True, True]
    assert start_indices == [0, 4]
