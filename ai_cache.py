"""
Simple file-based cache for AI responses
Reduces API costs by caching similar customer analyses
"""

import json
import os
import time
from typing import Optional, Any
from pathlib import Path


class AICache:
    """
    File-based cache for AI pattern analysis results
    """
    
    def __init__(self, cache_dir: str = '.ai_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache if exists and not expired"""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if expired
            if time.time() > data['expires_at']:
                cache_file.unlink()
                return None
            
            # Return the cached object (reconstruct PatternInsight)
            from ai_pattern_analyzer import PatternInsight
            value_dict = data['value']
            if 'suggested_price_position' not in value_dict:
                rm = value_dict.get('risk_multiplier', 1.0)
                if rm > 1.5:
                    value_dict['suggested_price_position'] = 0.75
                elif rm < 0.9:
                    value_dict['suggested_price_position'] = 0.45
                else:
                    value_dict['suggested_price_position'] = 0.6
            return PatternInsight(**value_dict)
            
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Store in cache with TTL"""
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            # Convert PatternInsight to dict for serialization
            value_dict = {
                'pattern_description': value.pattern_description,
                'cohort_size': value.cohort_size,
                'claim_rate': value.claim_rate,
                'baseline_claim_rate': value.baseline_claim_rate,
                'risk_multiplier': value.risk_multiplier,
                'confidence': value.confidence,
                'key_factors': value.key_factors,
                'recommendation': value.recommendation,
                'statistical_significance': value.statistical_significance,
                'suggested_price_position': getattr(value, 'suggested_price_position', None)
            }
            
            data = {
                'value': value_dict,
                'expires_at': time.time() + ttl,
                'cached_at': time.time()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def clear_expired(self):
        """Remove expired cache entries"""
        now = time.time()
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                if now > data['expires_at']:
                    cache_file.unlink()
            except:
                pass
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = len(list(self.cache_dir.glob("*.json")))
        return {
            'total_entries': total,
            'cache_dir': str(self.cache_dir)
        }
