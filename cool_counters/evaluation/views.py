from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import pathlib

# Define paths relative to the project root
def get_paths():
    # Get the absolute path to the project root
    project_root = pathlib.Path('/app')
    # Alternative path calculation if project_root doesn't exist
    alt_project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    
    # Define data paths
    recommendation_log_path = project_root / "counter/data/data_online_eval/recommendationlog_2025-03.csv"
    rating_log_path = project_root / "counter/data/data_online_eval/ratelog_2025-03.csv"
    datalog_path = project_root / "counter/data/data_online_eval/datalog_2025-03.csv"
    
    # If the paths don't exist with the default project_root, try the alternative
    if not os.path.exists(recommendation_log_path):
        recommendation_log_path = alt_project_root / "counter/data/data_online_eval/recommendationlog_2025-03.csv"
        rating_log_path = alt_project_root / "counter/data/data_online_eval/ratelog_2025-03.csv"
        datalog_path = alt_project_root / "counter/data/data_online_eval/datalog_2025-03.csv"
    
    return recommendation_log_path, rating_log_path, datalog_path

def load_logs():
    """
    Load recommendation, rating, and watch logs into DataFrames.
    Returns (rec_df, rate_df, watch_df).
    """
    recommendation_log_path, rating_log_path, datalog_path = get_paths()
    rec_df, rate_df, watch_df = None, None, None

    if os.path.exists(recommendation_log_path):
        rec_df = pd.read_csv(recommendation_log_path)
        rec_df["time"] = pd.to_datetime(rec_df["time"], errors="coerce")

    if os.path.exists(rating_log_path):
        rate_df = pd.read_csv(rating_log_path)
        rate_df["time"] = pd.to_datetime(rate_df["time"], errors="coerce")

    if os.path.exists(datalog_path):
        watch_df = pd.read_csv(datalog_path)
        watch_df["time"] = pd.to_datetime(watch_df["time"], errors="coerce")

    return rec_df, rate_df, watch_df

def parse_timeframe_param(timeframe_str):
    """
    Convert timeframe strings like 'LastHour' or 'Last7Days' to a timedelta.
    """
    tf = timeframe_str.strip().lower()
    if tf == "lasthour":
        return timedelta(hours=1)
    elif tf == "last24hours":
        return timedelta(hours=24)
    elif tf == "last7days":
        return timedelta(days=7)
    else:
        return timedelta(hours=1)  # default

def filter_dataframes_by_time(rec_df, rate_df, watch_df, cutoff_time, log_now):
    """
    Filters the dataframes to include only rows within the specified time range.
    """
    rec_df = rec_df[(rec_df["time"] >= cutoff_time) & (rec_df["time"] <= log_now)]
    if not rate_df.empty:
        rate_df = rate_df[(rate_df["time"] >= cutoff_time) & (rate_df["time"] <= log_now)]
    if not watch_df.empty:
        watch_df = watch_df[(watch_df["time"] >= cutoff_time) & (watch_df["time"] <= log_now)]
    return rec_df, rate_df, watch_df

def calculate_rating_metrics(rec_expanded, rate_df):
    """
    Calculates rating-related metrics.
    """
    merged_ratings = pd.merge(
        rec_expanded,
        rate_df,
        how="inner",
        on=["user_id", "movie_id"]
    ) if not rate_df.empty else pd.DataFrame()

    num_rated_recs = len(merged_ratings)
    mean_rating = merged_ratings["rating"].mean() if not merged_ratings.empty else None
    rating_variance = merged_ratings["rating"].var(ddof=1) if not merged_ratings.empty else None
    rating_distribution = merged_ratings["rating"].value_counts().sort_index().to_dict() if not merged_ratings.empty else {}

    return num_rated_recs, mean_rating, rating_variance, rating_distribution

def calculate_watch_metrics(rec_expanded, watch_df):
    """
    Calculates watch time-related metrics.
    """
    if watch_df.empty:
        return 0, 0.0, 0.0

    watch_agg = watch_df.groupby(["user_id", "movie_id"])["minute"].max().reset_index(name="watch_time")
    rec_watch_merged = pd.merge(
        rec_expanded,
        watch_agg,
        how="inner",
        on=["user_id", "movie_id"]
    )
    watched_recs = len(rec_watch_merged)
    avg_watch_time = rec_watch_merged["watch_time"].mean() if watched_recs > 0 else 0.0
    watch_coverage = watched_recs / len(rec_expanded) if len(rec_expanded) > 0 else 0.0

    return watched_recs, avg_watch_time, watch_coverage

def compute_metrics(timeframe="LastHour"):
    """
    Extended version that also considers watch time from datalog.
    """
    rec_df, rate_df, watch_df = load_logs()
    # Basic validation
    if rec_df is None or rec_df.empty:
        return {"error": "No recommendation logs found", "num_recs": 0}
    if rate_df is None or rate_df.empty:
        rate_df = pd.DataFrame(columns=["movie_id", "rating", "time", "user_id"])
    if watch_df is None or watch_df.empty:
        watch_df = pd.DataFrame(columns=["minute", "movie_id", "time", "user_id"])

    # 1) Find latest timestamps to anchor 'log_now'
    max_rec_time  = rec_df["time"].max()
    max_rate_time = rate_df["time"].max() if not rate_df.empty else pd.NaT
    max_watch_time= watch_df["time"].max() if not watch_df.empty else pd.NaT

    # If we have no valid timestamps, bail out
    if pd.isna(max_rec_time) and pd.isna(max_rate_time) and pd.isna(max_watch_time):
        return {"error": "Logs have no valid timestamps", "num_recs": 0}

    log_now = max(t for t in [max_rec_time, max_rate_time, max_watch_time] if not pd.isna(t))
    delta = parse_timeframe_param(timeframe)
    cutoff_time = log_now - delta

    # 2) Filter all DataFrames to [cutoff_time, log_now]
    rec_df, rate_df, watch_df = filter_dataframes_by_time(rec_df, rate_df, watch_df, cutoff_time, log_now)

    if rec_df.empty:
        return {
            "error": "No recommendations found in that timeframe.",
            "num_recs": 0,
            "num_rated_recs": 0,
            "mean_rating": None,
            "rating_variance": None,
            "rating_distribution": {},
            # watch stats
            "watched_recs": 0,
            "avg_watch_time": 0.0,
            "watch_coverage": 0.0
        }

    # 3) Explode recommended movies
    rec_df["recommended_movies"] = rec_df["result"].astype(str).apply(lambda x: x.split(';'))
    rec_expanded = rec_df.explode("recommended_movies").rename(columns={"recommended_movies": "movie_id"})
    num_recs = len(rec_expanded)

    # 4) Calculate metrics
    num_rated_recs, mean_rating, rating_variance, rating_distribution = calculate_rating_metrics(rec_expanded, rate_df)
    watched_recs, avg_watch_time, watch_coverage = calculate_watch_metrics(rec_expanded, watch_df)

    # 5) Build final results dictionary
    results = {
        "error": None,
        "num_recs": num_recs,
        # Ratings
        "num_rated_recs": num_rated_recs,
        "mean_rating": round(mean_rating, 3) if mean_rating is not None else None,
        "rating_variance": round(rating_variance, 3) if rating_variance is not None and not np.isnan(rating_variance) else None,
        "rating_distribution": rating_distribution,
        # Watch time
        "watched_recs": watched_recs,
        "avg_watch_time": round(avg_watch_time, 2),
        "watch_coverage": round(watch_coverage, 3)
    }
    # If no recommended movies at all
    if num_recs == 0:
        results["error"] = "No recommended movies in timeframe"
    # If we had no rating or watch data
    if num_rated_recs == 0 and watched_recs == 0:
        results["error"] = "No recommended movies were rated or watched in that timeframe."

    return results

# Django view functions

def home(request):
    """Home page of the evaluation dashboard"""
    return render(request, 'evaluation/index.html')

def evaluate(request):
    """Evaluate metrics based on selected timeframe"""
    timeframe = request.GET.get("timeframe", "LastHour")
    results = compute_metrics(timeframe)
    
    # Add the timeframe to the results for the template
    context = results.copy()
    context['timeframe'] = timeframe
    
    return render(request, 'evaluation/index.html', context)

def health(request):
    """Simple health check endpoint"""
    return HttpResponse('OK')
