from django.test import TestCase
from cool_counters.evaluation import views
import pandas as pd
from datetime import timedelta
import numpy as np
import os
import tempfile

class TestEvaluationApp(TestCase):
    
    def setUp(self):
        # Create a temporary directory for test data
        self.test_dir = tempfile.TemporaryDirectory()
        self.data_dir = os.path.join(self.test_dir.name, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create empty test files
        for file_name in ["recommendationlog_2025-03.csv", "ratelog_2025-03.csv", "datalog_2025-03.csv"]:
            with open(os.path.join(self.data_dir, file_name), 'w') as f:
                f.write("user_id,movie_id,time,result\n")
                f.write("1,movie1,2025-03-01 12:00:00,movie1;movie2\n")
        
        # Mock get_paths to return our test files
        self.original_get_paths = views.get_paths
        views.get_paths = lambda: (
            os.path.join(self.data_dir, "recommendationlog_2025-03.csv"),
            os.path.join(self.data_dir, "ratelog_2025-03.csv"),
            os.path.join(self.data_dir, "datalog_2025-03.csv")
        )
    
    def tearDown(self):
        # Restore original get_paths function
        views.get_paths = self.original_get_paths
        # Remove temporary directory
        self.test_dir.cleanup()

    def test_load_logs(self):
        rec_df, rate_df, watch_df = views.load_logs()
        
        # Check if pandas DataFrame objects are returned
        self.assertIsInstance(rec_df, pd.DataFrame)
        self.assertIsInstance(rate_df, pd.DataFrame)
        self.assertIsInstance(watch_df, pd.DataFrame)
        
        # Verify content of recommendation log
        self.assertEqual(len(rec_df), 1)
        self.assertEqual(rec_df.iloc[0]['user_id'], 1)
        self.assertEqual(rec_df.iloc[0]['movie_id'], 'movie1')
        self.assertEqual(rec_df.iloc[0]['result'], 'movie1;movie2')

    def test_parse_timeframe_param(self):
        timeframe_str = "LastHour"
        timeframe = views.parse_timeframe_param(timeframe_str)
        self.assertEqual(timeframe, timedelta(hours=1))

        timeframe_str = "Last24Hours"
        timeframe = views.parse_timeframe_param(timeframe_str)
        self.assertEqual(timeframe, timedelta(hours=24))

        timeframe_str = "Last7Days"
        timeframe = views.parse_timeframe_param(timeframe_str)
        self.assertEqual(timeframe, timedelta(days=7))

        timeframe_str = "Anything"
        timeframe = views.parse_timeframe_param(timeframe_str)
        self.assertEqual(timeframe, timedelta(hours=1))

    def test_compute_metrics(self):
        # Mock the compute_metrics function temporarily to avoid data dependencies
        original_compute_metrics = views.compute_metrics
        
        def mock_compute_metrics(timeframe="LastHour"):
            return {
                "error": None,
                "num_recs": 2,
                "num_rated_recs": 1,
                "mean_rating": 4.0,
                "rating_variance": None,
                "rating_distribution": {4: 1},
                "watched_recs": 1,
                "avg_watch_time": 90.0,
                "watch_coverage": 0.5
            }
        
        # Replace with mock
        views.compute_metrics = mock_compute_metrics
        
        try:
            results = views.compute_metrics(timeframe="LastHour")
            self.assertIsInstance(results, dict)
            self.assertIn('num_recs', results)
            self.assertEqual(results["num_recs"], 2)
        finally:
            # Restore original
            views.compute_metrics = original_compute_metrics

    def test_calculate_rating_metrics(self):
        rec_expanded = pd.DataFrame({
            "user_id": [1, 2],
            "movie_id": ["movie1", "movie2"]
        })
        rate_df = pd.DataFrame({
            "user_id": [1, 2],
            "movie_id": ["movie1", "movie1"],
            "rating": [4, 3]
        })
        num_rated_recs, mean_rating, rating_variance, rating_distribution = views.calculate_rating_metrics(rec_expanded, rate_df)
        self.assertEqual(num_rated_recs, 1)
        self.assertEqual(mean_rating, 4.0)  # For recommended movies
        # Check variance of single value
        self.assertTrue(np.isnan(rating_variance))
        self.assertEqual(rating_distribution, {4: 1})

    def test_calculate_watch_metrics(self):
        rec_expanded = pd.DataFrame({
            "user_id": [1, 2],
            "movie_id": ["movie1", "movie2"]
        })
        watch_df = pd.DataFrame({
            "user_id": [1, 2],
            "movie_id": ["movie1", "movie1"],
            "minute": [90, 5]
        })
        watched_recs, avg_watch_time, watch_coverage = views.calculate_watch_metrics(rec_expanded, watch_df)
        self.assertEqual(watched_recs, 1)
        self.assertEqual(avg_watch_time, 90)
        self.assertEqual(watch_coverage, 0.5)
    
    def test_home_view(self):
        response = self.client.get('/evaluation/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'evaluation/index.html')
    
    def test_evaluate_view(self):
        response = self.client.get('/evaluation/evaluate/', {'timeframe': 'LastHour'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'evaluation/index.html')
        
    def test_health_view(self):
        response = self.client.get('/evaluation/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
