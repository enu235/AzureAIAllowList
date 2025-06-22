import sys
from typing import Optional, Dict, Any, List
from datetime import datetime

class ProgressTracker:
    """Track and display progress of connectivity analysis"""
    
    def __init__(self, total_steps: int, verbose: bool = False):
        self.total_steps = total_steps
        self.current_step = 0
        self.verbose = verbose
        self.start_time = datetime.now()
        self.step_details: List[Dict[str, Any]] = []
        
    def start_step(self, step_name: str, description: str = ""):
        """Start a new analysis step"""
        self.current_step += 1
        step_info = {
            'step': self.current_step,
            'name': step_name,
            'description': description,
            'start_time': datetime.now(),
            'status': 'in_progress'
        }
        self.step_details.append(step_info)
        self._display_progress(step_name, description)
        
    def complete_step(self, success: bool = True, message: str = ""):
        """Mark current step as complete"""
        if self.step_details:
            current = self.step_details[-1]
            current['end_time'] = datetime.now()
            current['duration'] = (current['end_time'] - current['start_time']).total_seconds()
            current['status'] = 'success' if success else 'failed'
            current['message'] = message
            
    def _display_progress(self, step_name: str, description: str):
        """Display progress to user"""
        progress = f"[{self.current_step}/{self.total_steps}]"
        if self.verbose:
            print(f"{progress} {step_name}: {description}")
        else:
            print(f"{progress} {step_name}")
            
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all steps"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        successful_steps = sum(1 for s in self.step_details if s.get('status') == 'success')
        failed_steps = sum(1 for s in self.step_details if s.get('status') == 'failed')
        
        return {
            'total_duration': total_duration,
            'total_steps': self.total_steps,
            'completed_steps': len(self.step_details),
            'successful_steps': successful_steps,
            'failed_steps': failed_steps,
            'step_details': self.step_details
        } 