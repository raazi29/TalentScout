"""
Performance Manager for TalentScout Hiring Assistant.

Handles response optimization, caching, and efficient processing.
"""
import time
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable
from collections import OrderedDict
import json
import os
from datetime import datetime, timedelta
import hashlib

class PerformanceManager:
    """Manages performance optimization for the TalentScout chatbot."""
    
    def __init__(self, cache_size: int = 100, cache_ttl: int = 3600):
        """
        Initialize the performance manager.
        
        Args:
            cache_size: Maximum number of cached items
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.response_cache = OrderedDict()
        self.request_queue = []
        self.processing_threads = []
        self.max_concurrent_requests = 5
        self.request_semaphore = threading.Semaphore(self.max_concurrent_requests)
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0,
            "response_times": [],
            "error_count": 0
        }
        
        # Start background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_cache, daemon=True)
        self.cleanup_thread.start()
    
    def get_cached_response(self, key: str) -> Optional[str]:
        """
        Get a cached response if available and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response or None if not found/expired
        """
        if key in self.response_cache:
            cached_item = self.response_cache[key]
            
            # Check if cache item is expired
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                # Move to end (most recently used)
                self.response_cache.move_to_end(key)
                self.metrics["cache_hits"] += 1
                return cached_item["response"]
            else:
                # Remove expired item
                del self.response_cache[key]
        
        self.metrics["cache_misses"] += 1
        return None
    
    def cache_response(self, key: str, response: str) -> None:
        """
        Cache a response with timestamp.
        
        Args:
            key: Cache key
            response: Response to cache
        """
        # Remove oldest item if cache is full
        if len(self.response_cache) >= self.cache_size:
            self.response_cache.popitem(last=False)
        
        # Add new item
        self.response_cache[key] = {
            "response": response,
            "timestamp": time.time()
        }
    
    def generate_cache_key(self, prompt: str, user_context: Dict) -> str:
        """
        Generate a cache key based on prompt and user context.
        
        Args:
            prompt: The prompt text
            user_context: User context information
            
        Returns:
            Cache key string
        """
        # Create a hash of prompt and relevant context
        context_str = json.dumps(user_context, sort_keys=True)
        combined = f"{prompt}:{context_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def optimize_prompt(self, prompt: str, user_context: Dict) -> str:
        """
        Optimize prompt for better performance and relevance.
        
        Args:
            prompt: Original prompt
            user_context: User context information
            
        Returns:
            Optimized prompt
        """
        # Add context-aware optimizations
        optimized_prompt = prompt
        
        # Add user experience level context
        if "years_experience" in user_context:
            years = user_context["years_experience"]
            if years >= 5:
                optimized_prompt += "\n\nNote: This candidate has senior-level experience. Provide detailed, advanced-level responses."
            elif years >= 2:
                optimized_prompt += "\n\nNote: This candidate has mid-level experience. Provide balanced responses."
            else:
                optimized_prompt += "\n\nNote: This candidate has junior-level experience. Provide clear, educational responses."
        
        # Add language preference context
        if "language" in user_context and user_context["language"] != "en":
            optimized_prompt += f"\n\nPlease respond in {user_context['language']}."
        
        # Add communication style preference
        if "communication_style" in user_context:
            style = user_context["communication_style"]
            if style == "casual":
                optimized_prompt += "\n\nUse a friendly, casual tone in your responses."
            elif style == "formal":
                optimized_prompt += "\n\nUse a formal, professional tone in your responses."
        
        return optimized_prompt
    
    def process_request_async(self, request_func: Callable, *args, **kwargs) -> Any:
        """
        Process a request asynchronously with performance monitoring.
        
        Args:
            request_func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        start_time = time.time()
        
        try:
            with self.request_semaphore:
                result = request_func(*args, **kwargs)
                
                # Record response time
                response_time = time.time() - start_time
                self._record_response_time(response_time)
                
                return result
                
        except Exception as e:
            self.metrics["error_count"] += 1
            raise e
        finally:
            self.metrics["total_requests"] += 1
    
    def _record_response_time(self, response_time: float) -> None:
        """
        Record response time for metrics calculation.
        
        Args:
            response_time: Response time in seconds
        """
        self.metrics["response_times"].append(response_time)
        
        # Keep only last 100 response times
        if len(self.metrics["response_times"]) > 100:
            self.metrics["response_times"] = self.metrics["response_times"][-100:]
        
        # Update average response time
        self.metrics["average_response_time"] = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
    
    def _cleanup_cache(self) -> None:
        """Background thread to clean up expired cache entries."""
        while True:
            try:
                current_time = time.time()
                expired_keys = []
                
                for key, item in self.response_cache.items():
                    if current_time - item["timestamp"] >= self.cache_ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.response_cache[key]
                
                # Sleep for 5 minutes before next cleanup
                time.sleep(300)
                
            except Exception as e:
                print(f"Cache cleanup error: {e}")
                time.sleep(60)  # Sleep for 1 minute on error
    
    def get_performance_metrics(self) -> Dict:
        """
        Get current performance metrics.
        
        Returns:
            Performance metrics dictionary
        """
        cache_hit_rate = 0
        if self.metrics["total_requests"] > 0:
            cache_hit_rate = (self.metrics["cache_hits"] / 
                            (self.metrics["cache_hits"] + self.metrics["cache_misses"])) * 100
        
        return {
            "total_requests": self.metrics["total_requests"],
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "cache_hit_rate": cache_hit_rate,
            "average_response_time": self.metrics["average_response_time"],
            "error_count": self.metrics["error_count"],
            "cache_size": len(self.response_cache),
            "active_threads": len(self.processing_threads)
        }
    
    def optimize_batch_requests(self, requests: List[Dict]) -> List[Dict]:
        """
        Optimize a batch of requests for better performance.
        
        Args:
            requests: List of request dictionaries
            
        Returns:
            Optimized list of requests
        """
        optimized_requests = []
        
        # Group similar requests
        request_groups = {}
        for request in requests:
            request_type = request.get("type", "general")
            if request_type not in request_groups:
                request_groups[request_type] = []
            request_groups[request_type].append(request)
        
        # Process each group
        for request_type, group_requests in request_groups.items():
            if request_type == "technical_questions":
                # Optimize technical question generation
                optimized_requests.extend(self._optimize_technical_questions(group_requests))
            elif request_type == "information_gathering":
                # Optimize information gathering
                optimized_requests.extend(self._optimize_information_gathering(group_requests))
            else:
                # General requests
                optimized_requests.extend(group_requests)
        
        return optimized_requests
    
    def _optimize_technical_questions(self, requests: List[Dict]) -> List[Dict]:
        """
        Optimize technical question requests.
        
        Args:
            requests: List of technical question requests
            
        Returns:
            Optimized requests
        """
        # Combine similar tech stack requests
        tech_stack_groups = {}
        
        for request in requests:
            tech_stack = tuple(sorted(request.get("tech_stack", [])))
            if tech_stack not in tech_stack_groups:
                tech_stack_groups[tech_stack] = []
            tech_stack_groups[tech_stack].append(request)
        
        optimized_requests = []
        
        for tech_stack, group_requests in tech_stack_groups.items():
            if len(group_requests) > 1:
                # Combine multiple requests for the same tech stack
                combined_request = {
                    "type": "technical_questions",
                    "tech_stack": list(tech_stack),
                    "years_experience": max(req.get("years_experience", 0) for req in group_requests),
                    "combined_requests": len(group_requests)
                }
                optimized_requests.append(combined_request)
            else:
                optimized_requests.extend(group_requests)
        
        return optimized_requests
    
    def _optimize_information_gathering(self, requests: List[Dict]) -> List[Dict]:
        """
        Optimize information gathering requests.
        
        Args:
            requests: List of information gathering requests
            
        Returns:
            Optimized requests
        """
        # Prioritize requests based on conversation flow
        prioritized_requests = sorted(requests, key=lambda x: x.get("priority", 0), reverse=True)
        
        # Remove redundant requests
        seen_fields = set()
        optimized_requests = []
        
        for request in prioritized_requests:
            fields = request.get("fields", [])
            new_fields = [field for field in fields if field not in seen_fields]
            
            if new_fields:
                request["fields"] = new_fields
                optimized_requests.append(request)
                seen_fields.update(new_fields)
        
        return optimized_requests
    
    def preload_common_responses(self) -> None:
        """Preload common responses into cache for faster access."""
        common_prompts = [
            "greeting",
            "name_collection",
            "contact_collection",
            "experience_collection",
            "position_collection",
            "location_collection",
            "tech_stack_collection",
            "farewell"
        ]
        
        for prompt_type in common_prompts:
            key = f"common_{prompt_type}"
            # Add placeholder responses that will be replaced with actual content
            self.cache_response(key, f"Common response for {prompt_type}")
    
    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self.response_cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """
        Get detailed cache statistics.
        
        Returns:
            Cache statistics dictionary
        """
        cache_ages = []
        for item in self.response_cache.values():
            cache_ages.append(time.time() - item["timestamp"])
        
        return {
            "total_items": len(self.response_cache),
            "oldest_item_age": max(cache_ages) if cache_ages else 0,
            "newest_item_age": min(cache_ages) if cache_ages else 0,
            "average_item_age": sum(cache_ages) / len(cache_ages) if cache_ages else 0
        } 