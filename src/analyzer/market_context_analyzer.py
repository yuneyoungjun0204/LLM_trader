"""
Market Context Analyzer - Builds structured market context from multi-timeframe data.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class MarketContextAnalyzer:
    """Analyzes market context from multi-timeframe data and divergence signals."""
    
    @staticmethod
    def build_market_context(
        mtf_data: Dict[str, Any],
        divergence_data: Dict[str, Any],
        filter_tf_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Build structured market context from multi-timeframe data.
        
        Args:
            mtf_data: Multi-timeframe data dictionary
            divergence_data: Divergence signals dictionary
            filter_tf_df: Filter timeframe DataFrame (optional)
        
        Returns:
            Dictionary with market context including regime, stochastic, BB, divergence states
        """
        # Initialize default context
        context = {
            'regime': {
                'regime_type': 'NEUTRAL',
                'trend_strength': 0.0,
                'regime_confidence': 0.0
            },
            'stochastic': {
                'state': 'neutral'
            },
            'bollinger_bands': {
                'state': 'neutral'
            },
            'divergence': {
                'state': 'none',
                'strength': 0.0
            }
        }
        
        # Extract regime information from MTF data
        try:
            regime_info = MarketContextAnalyzer._analyze_regime(mtf_data)
            context['regime'].update(regime_info)
        except Exception:
            pass
        
        # Extract stochastic state
        try:
            if filter_tf_df is not None and 'stoch_k' in filter_tf_df.columns:
                stoch_k = filter_tf_df['stoch_k'].iloc[-1] if len(filter_tf_df) > 0 else 50.0
                if stoch_k > 80:
                    context['stochastic']['state'] = 'overbought'
                elif stoch_k < 20:
                    context['stochastic']['state'] = 'oversold'
                else:
                    context['stochastic']['state'] = 'neutral'
        except Exception:
            pass
        
        # Extract Bollinger Bands state
        try:
            if filter_tf_df is not None and 'bb_middleband' in filter_tf_df.columns and 'close' in filter_tf_df.columns:
                close = filter_tf_df['close'].iloc[-1] if len(filter_tf_df) > 0 else 0.0
                bb_middle = filter_tf_df['bb_middleband'].iloc[-1] if len(filter_tf_df) > 0 else 0.0
                
                if close > bb_middle:
                    context['bollinger_bands']['state'] = 'above_middle'
                elif close < bb_middle:
                    context['bollinger_bands']['state'] = 'below_middle'
                else:
                    context['bollinger_bands']['state'] = 'at_middle'
        except Exception:
            pass
        
        # Extract divergence state
        try:
            divergence_state = MarketContextAnalyzer._analyze_divergence(divergence_data)
            context['divergence'].update(divergence_state)
        except Exception:
            pass
        
        return context
    
    @staticmethod
    def _analyze_regime(mtf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market regime from multi-timeframe data.
        
        Args:
            mtf_data: Multi-timeframe data dictionary
        
        Returns:
            Dictionary with regime_type, trend_strength, regime_confidence
        """
        regime_info = {
            'regime_type': 'NEUTRAL',
            'trend_strength': 0.0,
            'regime_confidence': 0.0
        }
        
        if not mtf_data:
            return regime_info
        
        bullish_count = 0
        bearish_count = 0
        total_timeframes = 0
        trend_strengths = []
        
        # Analyze each timeframe
        for timeframe, data in mtf_data.items():
            if data is None:
                continue
            
            try:
                # Extract OHLCV and close series
                if isinstance(data, tuple):
                    ohlcv, close_series = data
                else:
                    # Assume it's a DataFrame
                    if hasattr(data, 'values'):
                        ohlcv = data[['open', 'high', 'low', 'close', 'volume']].values
                        close_series = data['close'].values
                    else:
                        continue
                
                if len(close_series) < 20:
                    continue
                
                # Simple trend analysis: compare recent vs older prices
                recent_price = float(close_series[-1])
                older_price = float(close_series[-20]) if len(close_series) >= 20 else recent_price
                
                price_change_pct = ((recent_price - older_price) / older_price) * 100 if older_price > 0 else 0.0
                
                trend_strengths.append(abs(price_change_pct))
                
                if price_change_pct > 1.0:  # Bullish
                    bullish_count += 1
                elif price_change_pct < -1.0:  # Bearish
                    bearish_count += 1
                
                total_timeframes += 1
            except Exception:
                continue
        
        if total_timeframes == 0:
            return regime_info
        
        # Determine regime
        bullish_ratio = bullish_count / total_timeframes if total_timeframes > 0 else 0.0
        bearish_ratio = bearish_count / total_timeframes if total_timeframes > 0 else 0.0
        
        avg_strength = sum(trend_strengths) / len(trend_strengths) if trend_strengths else 0.0
        
        if bullish_ratio > 0.6:
            regime_info['regime_type'] = 'BULLISH'
            regime_info['trend_strength'] = avg_strength
            regime_info['regime_confidence'] = bullish_ratio * 100
        elif bearish_ratio > 0.6:
            regime_info['regime_type'] = 'BEARISH'
            regime_info['trend_strength'] = avg_strength
            regime_info['regime_confidence'] = bearish_ratio * 100
        else:
            regime_info['regime_type'] = 'NEUTRAL'
            regime_info['trend_strength'] = avg_strength
            regime_info['regime_confidence'] = max(bullish_ratio, bearish_ratio) * 100
        
        return regime_info
    
    @staticmethod
    def _analyze_divergence(divergence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze divergence signals.
        
        Args:
            divergence_data: Divergence signals dictionary
        
        Returns:
            Dictionary with divergence state and strength
        """
        divergence_info = {
            'state': 'none',
            'strength': 0.0
        }
        
        if not divergence_data:
            return divergence_info
        
        # Check for divergence signals
        has_bullish = divergence_data.get('stoch_hidden_bullish', False) or \
                     divergence_data.get('stoch_regular_bullish', False)
        has_bearish = divergence_data.get('stoch_hidden_bearish', False) or \
                     divergence_data.get('stoch_regular_bearish', False)
        
        if has_bullish and not has_bearish:
            divergence_info['state'] = 'bullish'
            divergence_info['strength'] = 70.0  # Moderate strength
        elif has_bearish and not has_bullish:
            divergence_info['state'] = 'bearish'
            divergence_info['strength'] = 70.0  # Moderate strength
        elif has_bullish and has_bearish:
            divergence_info['state'] = 'mixed'
            divergence_info['strength'] = 30.0  # Low strength (conflicting signals)
        else:
            divergence_info['state'] = 'none'
            divergence_info['strength'] = 0.0
        
        return divergence_info

