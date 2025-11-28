#!/usr/bin/env python3
"""
Smart Task Analyzer - Command Line Version
"""
import json
import sys
from datetime import datetime, date
from typing import List, Dict, Any

class TaskScorer:
    def __init__(self, strategy: str = "4"):
        self.strategy = strategy
        self.weights = self._get_weights(strategy)
    
    def _get_weights(self, strategy: str) -> Dict[str, float]:
        weights_map = {
            "1": {"effort": 0.6, "urgency": 0.2, "importance": 0.2},
            "2": {"importance": 0.7, "urgency": 0.2, "effort": 0.1},
            "3": {"urgency": 0.8, "importance": 0.15, "effort": 0.05},
            "4": {"urgency": 0.4, "importance": 0.4, "effort": 0.2}
        }
        return weights_map.get(strategy, weights_map["4"])
    
    def calculate_urgency_score(self, due_date: str) -> float:
        try:
            due = datetime.strptime(due_date, '%Y-%m-%d').date()
            today = date.today()
            days_until_due = (due - today).days
            
            if days_until_due < 0:
                return 1.0
            elif days_until_due == 0:
                return 0.9
            elif days_until_due <= 1:
                return 0.8
            elif days_until_due <= 3:
                return 0.6
            elif days_until_due <= 7:
                return 0.4
            else:
                return 0.2
        except ValueError:
            return 0.1
    
    def calculate_effort_score(self, estimated_hours: float) -> float:
        if estimated_hours <= 1:
            return 1.0
        elif estimated_hours <= 2:
            return 0.8
        elif estimated_hours <= 4:
            return 0.6
        elif estimated_hours <= 8:
            return 0.4
        else:
            return 0.2
    
    def calculate_importance_score(self, importance: int) -> float:
        if 1 <= importance <= 10:
            return importance / 10.0
        return 0.1
    
    def calculate_dependency_boost(self, dependencies: List[str], all_tasks: List[Dict]) -> float:
        if not dependencies:
            return 0.0
        
        blocking_count = 0
        for task in all_tasks:
            task_deps = task.get('dependencies', [])
            if any(dep in dependencies for dep in task_deps):
                blocking_count += 1
        
        return min(blocking_count * 0.1, 0.3)
    
    def calculate_score(self, task: Dict[str, Any], all_tasks: List[Dict]) -> float:
        try:
            urgency_score = self.calculate_urgency_score(task['due_date'])
            effort_score = self.calculate_effort_score(task['estimated_hours'])
            importance_score = self.calculate_importance_score(task['importance'])
            
            dependency_boost = self.calculate_dependency_boost(
                task.get('dependencies', []), all_tasks
            )
            
            base_score = (
                urgency_score * self.weights['urgency'] +
                effort_score * self.weights['effort'] +
                importance_score * self.weights['importance']
            )
            
            final_score = min(base_score + dependency_boost, 1.0)
            return round(final_score, 2)
            
        except (KeyError, TypeError) as e:
            return 0.0
    
    def get_score_explanation(self, task: Dict[str, Any], score: float, all_tasks: List[Dict]) -> str:
        explanations = []
        
        urgency = self.calculate_urgency_score(task['due_date'])
        effort = self.calculate_effort_score(task['estimated_hours'])
        importance = self.calculate_importance_score(task['importance'])
        
        if urgency >= 0.8:
            explanations.append("🚨 HIGH URGENCY")
        elif urgency >= 0.6:
            explanations.append("⚠️ Medium urgency")
        else:
            explanations.append("✅ Low urgency")
        
        if importance >= 0.8:
            explanations.append("⭐ HIGH IMPORTANCE")
        elif importance >= 0.6:
            explanations.append("📊 Medium importance")
        else:
            explanations.append("📝 Low importance")
        
        if effort >= 0.8:
            explanations.append("⚡ QUICK WIN")
        elif effort >= 0.6:
            explanations.append("🕒 Moderate effort")
        else:
            explanations.append("💪 High effort")
        
        dependencies = task.get('dependencies', [])
        if dependencies:
            explanations.append(f"🔗 Blocks {len(dependencies)} tasks")
        
        return " | ".join(explanations)

class TaskAnalyzer:
    def __init__(self):
        self.tasks = []
        self.strategy_names = {
            "1": "Fastest Wins",
            "2": "High Impact", 
            "3": "Deadline Driven",
            "4": "Smart Balance"
        }
    
    def display_menu(self):
        print("\n" + "="*60)
        print("🎯 SMART TASK ANALYZER")
        print("="*60)
        print("1. Add Task")
        print("2. Load Sample Tasks")
        print("3. Analyze & Prioritize Tasks")
        print("4. Change Strategy (Current: {})".format(
            self.strategy_names.get("4", "Smart Balance")
        ))
        print("5. View All Tasks")
        print("6. Clear All Tasks")
        print("7. Exit")
        print("="*60)
    
    def add_task(self):
        print("\n➕ ADD NEW TASK")
        print("-" * 30)
        
        title = input("Task title: ").strip()
        if not title:
            print("❌ Title is required!")
            return
        
        due_date = input("Due date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid date format! Use YYYY-MM-DD")
            return
        
        try:
            estimated_hours = float(input("Estimated hours: ").strip())
            importance = int(input("Importance (1-10): ").strip())
        except ValueError:
            print("❌ Hours must be a number, Importance must be 1-10!")
            return
        
        if not (1 <= importance <= 10):
            print("❌ Importance must be between 1-10!")
            return
        
        dependencies = input("Dependencies (comma-separated task IDs, or leave empty): ").strip()
        dependency_list = [dep.strip() for dep in dependencies.split(",")] if dependencies else []
        
        task = {
            "id": f"task{len(self.tasks) + 1}",
            "title": title,
            "due_date": due_date,
            "estimated_hours": estimated_hours,
            "importance": importance,
            "dependencies": dependency_list
        }
        
        self.tasks.append(task)
        print(f"✅ Task '{title}' added successfully!")
    
    def load_sample_tasks(self):
        sample_tasks = [
            {
                "id": "task1",
                "title": "Fix login bug",
                "due_date": "2024-12-01",
                "estimated_hours": 3,
                "importance": 8,
                "dependencies": []
            },
            {
                "id": "task2", 
                "title": "Write documentation",
                "due_date": "2024-12-10",
                "estimated_hours": 5,
                "importance": 6,
                "dependencies": ["task1"]
            },
            {
                "id": "task3",
                "title": "Setup deployment pipeline",
                "due_date": "2024-11-28",
                "estimated_hours": 8,
                "importance": 9,
                "dependencies": []
            },
            {
                "id": "task4",
                "title": "Code review",
                "due_date": "2024-11-29", 
                "estimated_hours": 2,
                "importance": 7,
                "dependencies": ["task1"]
            }
        ]
        
        self.tasks = sample_tasks
        print("✅ Sample tasks loaded successfully!")
        self.view_all_tasks()
    
    def analyze_tasks(self, strategy="4"):
        if not self.tasks:
            print("❌ No tasks to analyze! Add some tasks first.")
            return
        
        print(f"\n🎯 ANALYZING TASKS - {self.strategy_names[strategy]}")
        print("-" * 50)
        
        scorer = TaskScorer(strategy)
        
        # Calculate scores for all tasks
        for task in self.tasks:
            task['priority_score'] = scorer.calculate_score(task, self.tasks)
            task['explanation'] = scorer.get_score_explanation(task, task['priority_score'], self.tasks)
        
        # Sort by priority score
        sorted_tasks = sorted(self.tasks, key=lambda x: x['priority_score'], reverse=True)
        
        # Display results
        for i, task in enumerate(sorted_tasks, 1):
            score = task['priority_score']
            color = "🟢" if score >= 0.7 else "🟡" if score >= 0.4 else "🔴"
            
            print(f"\n{color} #{i}: {task['title']} (Score: {score})")
            print(f"   📅 Due: {task['due_date']} | ⏱️ {task['estimated_hours']}h | ⭐ {task['importance']}/10")
            print(f"   📝 {task['explanation']}")
            
            if task.get('dependencies'):
                print(f"   🔗 Dependencies: {', '.join(task['dependencies'])}")
        
        # Show top 3 recommendations
        print(f"\n💡 TOP 3 RECOMMENDATIONS:")
        for i in range(min(3, len(sorted_tasks))):
            task = sorted_tasks[i]
            reason = "Highest priority score based on current strategy"
            print(f"   {i+1}. {task['title']} - {reason}")
    
    def change_strategy(self):
        print("\n📊 SELECT STRATEGY:")
        print("1. Fastest Wins (Prioritize low-effort tasks)")
        print("2. High Impact (Prioritize important tasks)") 
        print("3. Deadline Driven (Prioritize urgent tasks)")
        print("4. Smart Balance (Balance all factors)")
        
        choice = input("\nSelect strategy (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            self.analyze_tasks(choice)
        else:
            print("❌ Invalid choice! Using Smart Balance.")
            self.analyze_tasks("4")
    
    def view_all_tasks(self):
        if not self.tasks:
            print("❌ No tasks available!")
            return
        
        print(f"\n📋 ALL TASKS ({len(self.tasks)} total)")
        print("-" * 40)
        for i, task in enumerate(self.tasks, 1):
            print(f"{i}. {task['title']}")
            print(f"   ID: {task['id']} | Due: {task['due_date']} | Effort: {task['estimated_hours']}h | Importance: {task['importance']}/10")
            if task.get('dependencies'):
                print(f"   Dependencies: {', '.join(task['dependencies'])}")
            print()
    
    def clear_tasks(self):
        self.tasks = []
        print("✅ All tasks cleared!")
    
    def run(self):
        print("🚀 Starting Smart Task Analyzer...")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.load_sample_tasks()
            elif choice == "3":
                self.analyze_tasks()
            elif choice == "4":
                self.change_strategy()
            elif choice == "5":
                self.view_all_tasks()
            elif choice == "6":
                self.clear_tasks()
            elif choice == "7":
                print("\n👋 Thank you for using Smart Task Analyzer!")
                break
            else:
                print("❌ Invalid choice! Please enter 1-7.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    analyzer = TaskAnalyzer()
    analyzer.run()