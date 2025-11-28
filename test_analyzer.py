#!/usr/bin/env python3
"""
Unit Tests for Smart Task Analyzer
"""
import unittest
from datetime import datetime, date, timedelta
import sys
import os

# Add the current directory to Python path so we can import task_analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from task_analyzer import TaskScorer

class TestTaskScorer(unittest.TestCase):
    
    def setUp(self):
        self.scorer = TaskScorer("4")  # Smart Balance strategy
        self.today = date.today()
    
    def test_urgency_score_past_due(self):
        past_date = (self.today - timedelta(days=1)).strftime('%Y-%m-%d')
        score = self.scorer.calculate_urgency_score(past_date)
        self.assertEqual(score, 1.0)
    
    def test_urgency_score_today(self):
        today_str = self.today.strftime('%Y-%m-%d')
        score = self.scorer.calculate_urgency_score(today_str)
        self.assertEqual(score, 0.9)
    
    def test_urgency_score_tomorrow(self):
        tomorrow = (self.today + timedelta(days=1)).strftime('%Y-%m-%d')
        score = self.scorer.calculate_urgency_score(tomorrow)
        self.assertEqual(score, 0.8)
    
    def test_urgency_score_3_days(self):
        three_days = (self.today + timedelta(days=3)).strftime('%Y-%m-%d')
        score = self.scorer.calculate_urgency_score(three_days)
        self.assertEqual(score, 0.6)
    
    def test_urgency_score_future(self):
        future_date = (self.today + timedelta(days=10)).strftime('%Y-%m-%d')
        score = self.scorer.calculate_urgency_score(future_date)
        self.assertEqual(score, 0.2)
    
    def test_effort_score_quick(self):
        self.assertEqual(self.scorer.calculate_effort_score(0.5), 1.0)
        self.assertEqual(self.scorer.calculate_effort_score(1.0), 1.0)
    
    def test_effort_score_medium(self):
        self.assertEqual(self.scorer.calculate_effort_score(2.0), 0.8)
        self.assertEqual(self.scorer.calculate_effort_score(3.0), 0.6)
    
    def test_effort_score_high(self):
        self.assertEqual(self.scorer.calculate_effort_score(8.0), 0.4)
        self.assertEqual(self.scorer.calculate_effort_score(10.0), 0.2)
    
    def test_importance_score(self):
        self.assertEqual(self.scorer.calculate_importance_score(10), 1.0)
        self.assertEqual(self.scorer.calculate_importance_score(5), 0.5)
        self.assertEqual(self.scorer.calculate_importance_score(1), 0.1)
    
    def test_invalid_importance(self):
        self.assertEqual(self.scorer.calculate_importance_score(0), 0.1)
        self.assertEqual(self.scorer.calculate_importance_score(11), 0.1)
    
    def test_dependency_boost(self):
        task_with_deps = {'dependencies': ['task1', 'task2']}
        all_tasks = [
            {'dependencies': ['task1']},
            {'dependencies': ['task2']},
            {'dependencies': []}
        ]
        boost = self.scorer.calculate_dependency_boost(
            task_with_deps['dependencies'], all_tasks
        )
        self.assertEqual(boost, 0.2)
    
    def test_dependency_boost_max(self):
        task_with_deps = {'dependencies': ['task1', 'task2', 'task3', 'task4']}
        all_tasks = [
            {'dependencies': ['task1']},
            {'dependencies': ['task2']},
            {'dependencies': ['task3']},
            {'dependencies': ['task4']},
            {'dependencies': ['task1']},
            {'dependencies': ['task2']}
        ]
        boost = self.scorer.calculate_dependency_boost(
            task_with_deps['dependencies'], all_tasks
        )
        self.assertEqual(boost, 0.3)  # Max boost
    
    def test_complete_scoring(self):
        task = {
            'title': 'Test Task',
            'due_date': (self.today + timedelta(days=1)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        all_tasks = [task]
        
        score = self.scorer.calculate_score(task, all_tasks)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        explanation = self.scorer.get_score_explanation(task, score, all_tasks)
        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 0)
    
    def test_different_strategies(self):
        strategies = ["1", "2", "3", "4"]
        task = {
            'due_date': self.today.strftime('%Y-%m-%d'),
            'estimated_hours': 4,
            'importance': 7,
            'dependencies': []
        }
        
        for strategy in strategies:
            scorer = TaskScorer(strategy)
            score = scorer.calculate_score(task, [task])
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_invalid_date(self):
        score = self.scorer.calculate_urgency_score("invalid-date")
        self.assertEqual(score, 0.1)

if __name__ == '__main__':
    print("Running Smart Task Analyzer Tests...")
    print("=" * 50)
    unittest.main(verbosity=2)
