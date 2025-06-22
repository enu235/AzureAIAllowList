from typing import Dict, List, Optional
import os
from datetime import datetime

class ReportFormatter:
    """Utilities for formatting report elements"""
    
    @staticmethod
    def format_table(headers: List[str], rows: List[List[str]]) -> str:
        """Format data as Markdown table"""
        if not headers or not rows:
            return ""
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Build table
        table = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |\n"
        table += "| " + " | ".join("-" * w for w in widths) + " |\n"
        
        for row in rows:
            cells = []
            for i, (cell, width) in enumerate(zip(row, widths)):
                cells.append(str(cell).ljust(width))
            table += "| " + " | ".join(cells) + " |\n"
        
        return table
    
    @staticmethod
    def format_progress_bar(value: float, max_value: float = 100, width: int = 20) -> str:
        """Create ASCII progress bar"""
        if max_value == 0:
            return "[" + " " * width + "]"
        
        percentage = value / max_value
        filled = int(width * percentage)
        
        bar = "[" + "█" * filled + "░" * (width - filled) + "]"
        return f"{bar} {value:.1f}/{max_value}"
    
    @staticmethod
    def format_security_score(score: int) -> str:
        """Format security score with color indicators"""
        if score >= 80:
            return f"🟢 {score}/100 (High)"
        elif score >= 60:
            return f"🟡 {score}/100 (Medium)"
        else:
            return f"🔴 {score}/100 (Low)"
    
    @staticmethod
    def format_resource_count(count: int, total: int) -> str:
        """Format resource count with percentage"""
        if total == 0:
            return f"{count}"
        
        percentage = (count / total) * 100
        return f"{count}/{total} ({percentage:.1f}%)"
    
    @staticmethod
    def format_timestamp(timestamp: Optional[str] = None) -> str:
        """Format timestamp for reports"""
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                return timestamp
        else:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
    
    @staticmethod
    def format_list_items(items: List[str], prefix: str = "•") -> str:
        """Format list items with consistent prefix"""
        if not items:
            return "None"
        
        return "\n".join(f"{prefix} {item}" for item in items)
    
    @staticmethod
    def format_key_value_pairs(pairs: Dict[str, str], separator: str = ": ") -> str:
        """Format key-value pairs consistently"""
        if not pairs:
            return "None"
        
        return "\n".join(f"{key}{separator}{value}" for key, value in pairs.items())
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """Truncate text with ellipsis if too long"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_boolean_indicator(value: bool, true_indicator: str = "✅", false_indicator: str = "❌") -> str:
        """Format boolean value with visual indicators"""
        return true_indicator if value else false_indicator
    
    @staticmethod
    def format_risk_level(level: str) -> str:
        """Format risk level with appropriate emoji"""
        level_lower = level.lower()
        
        if level_lower in ['high', 'critical']:
            return f"🔴 {level}"
        elif level_lower in ['medium', 'moderate']:
            return f"🟡 {level}"
        elif level_lower in ['low', 'minimal']:
            return f"🟢 {level}"
        else:
            return f"⚪ {level}"
    
    @staticmethod
    def format_connection_type(conn_type: str) -> str:
        """Format connection type with appropriate emoji"""
        conn_lower = conn_type.lower()
        
        if 'private' in conn_lower:
            return f"🔒 {conn_type}"
        elif 'public' in conn_lower:
            return f"🌐 {conn_type}"
        elif 'service' in conn_lower:
            return f"🔗 {conn_type}"
        else:
            return f"📡 {conn_type}" 