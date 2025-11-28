from http.server import HTTPServer, SimpleHTTPRequestHandler 
import json 
from datetime import datetime, date 
 
class TaskScorer: 
    def __init__(self, strategy="smart_balance"): 
        self.strategy = strategy 
        self.weights = self.get_weights(strategy) 
    def get_weights(self, strategy): 
        weights = { 
            "fastest_wins": {"effort": 0.6, "urgency": 0.2, "importance": 0.2}, 
            "high_impact": {"importance": 0.7, "urgency": 0.2, "effort": 0.1}, 
            "deadline_driven": {"urgency": 0.8, "importance": 0.15, "effort": 0.05}, 
            "smart_balance": {"urgency": 0.4, "importance": 0.4, "effort": 0.2} 
        } 
        return weights.get(strategy, weights["smart_balance"]) 
