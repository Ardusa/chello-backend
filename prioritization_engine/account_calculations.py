# from datetime import datetime, timedelta
# import models

# def calculate_work_time(
#     start_time: str,
#     end_time: str,
#     weekly_times: dict = {
#         "Monday": [("08:00:00", "17:00:00")],
#         "Tuesday": [("08:00:00", "17:00:00")],
#         "Wednesday": [("08:00:00", "17:00:00")],
#         "Thursday": [("08:00:00", "17:00:00")],
#         "Friday": [("08:00:00", "17:00:00")],
#     },
# ) -> timedelta:
#     """
#     Calculate the total work time between two time periods.

#     :param start_time: Start time in the format "{day_of_week}, {hour}:{minute}:{second}, {YYYY-MM-DD}"
#     :param end_time: End time in the format "{day_of_week}, {hour}:{minute}:{second}, {YYYY-MM-DD}"
#     :param weekly_times: Dictionary with days of the week as keys and a list of tuples (clock_in, clock_out) as values
#     :return: Total work time as a timedelta object
#     """
#     # Define the format string
#     time_format = "%A, %H:%M:%S, %Y-%m-%d"

#     # Parse the start and end times
#     start_dt = datetime.strptime(start_time, time_format)
#     end_dt = datetime.strptime(end_time, time_format)

#     total_work_time = timedelta()

#     current_dt = start_dt
#     while current_dt <= end_dt:
#         day_of_week = current_dt.strftime("%A")
#         if day_of_week in weekly_times:
#             for clock_in, clock_out in weekly_times[day_of_week]:
#                 clock_in_dt = datetime.strptime(clock_in, "%H:%M:%S").replace(
#                     year=current_dt.year, month=current_dt.month, day=current_dt.day
#                 )
#                 clock_out_dt = datetime.strptime(clock_out, "%H:%M:%S").replace(
#                     year=current_dt.year, month=current_dt.month, day=current_dt.day
#                 )

#                 if clock_in_dt < start_dt:
#                     clock_in_dt = start_dt
#                 if clock_out_dt > end_dt:
#                     clock_out_dt = end_dt

#                 if clock_in_dt < clock_out_dt:
#                     total_work_time += clock_out_dt - clock_in_dt

#         current_dt += timedelta(days=1)

#     return total_work_time