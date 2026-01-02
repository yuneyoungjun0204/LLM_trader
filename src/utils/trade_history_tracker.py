"""
Trade History Tracker for analyzing past trade patterns and preventing repeated mistakes.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TradeResult:
    """Individual trade result record."""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    profit_loss_pct: float
    exit_reason: str
    direction: str  # 'LONG' or 'SHORT'
    confidence: float
    market_conditions: Dict[str, Any] = field(default_factory=dict)
    confluence_factors: Dict[str, Any] = field(default_factory=dict)


class TradeHistoryTracker:
    """Tracks trade history and identifies patterns to prevent repeated losses."""
    
    def __init__(self, max_history: int = 50):
        """Initialize trade history tracker.
        
        Args:
            max_history: Maximum number of trades to keep in memory
        """
        self.max_history = max_history
        self.trade_history: List[TradeResult] = []
    
    def add_trade_result(
        self,
        trade_entry: Dict[str, Any],
        trade_exit: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> None:
        """Add a completed trade to history.
        
        Args:
            trade_entry: Entry trade information
            trade_exit: Exit trade information
            outcome: Trade outcome (profit/loss, etc.)
        """
        try:
            # Extract entry information
            entry_time = trade_entry.get('open_date', datetime.now())
            if isinstance(entry_time, str):
                entry_time = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
            
            entry_price = trade_entry.get('open_rate', 0.0)
            direction = trade_entry.get('direction', 'LONG').upper()
            confidence = trade_entry.get('confidence', 50.0)
            
            # Extract exit information
            exit_time = trade_exit.get('close_date', datetime.now())
            if isinstance(exit_time, str):
                exit_time = datetime.fromisoformat(exit_time.replace('Z', '+00:00'))
            
            exit_price = trade_exit.get('exit_price', trade_exit.get('close_rate', 0.0))
            exit_reason = trade_exit.get('exit_reason', 'unknown')
            profit_loss_pct = outcome.get('profit_loss_pct', 0.0)
            
            # Create trade result
            trade_result = TradeResult(
                entry_time=entry_time,
                exit_time=exit_time,
                entry_price=entry_price,
                exit_price=exit_price,
                profit_loss_pct=profit_loss_pct,
                exit_reason=exit_reason,
                direction=direction,
                confidence=confidence,
                market_conditions=outcome.get('market_conditions', {}),
                confluence_factors=outcome.get('confluence_factors', {})
            )
            
            # Add to history (FIFO - oldest first out)
            self.trade_history.append(trade_result)
            if len(self.trade_history) > self.max_history:
                self.trade_history.pop(0)
        
        except Exception as e:
            # Silently fail to prevent breaking the strategy
            pass
    
    def check_similar_to_past_losses(
        self,
        current_signal: Dict[str, Any],
        market_context: Dict[str, Any],
        similarity_threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """Check if current signal is similar to past losing trades.
        
        Args:
            current_signal: Current AI decision signal
            market_context: Current market conditions
            similarity_threshold: Minimum similarity score to trigger warning (0.0-1.0)
        
        Returns:
            Warning dictionary if similar past loss found, None otherwise
        """
        if not self.trade_history:
            return None
        
        # Filter to only losing trades
        losing_trades = [
            trade for trade in self.trade_history
            if trade.profit_loss_pct < 0
        ]
        
        if not losing_trades:
            return None
        
        # Compare with most recent losing trades (last 10)
        recent_losses = losing_trades[-10:]
        
        current_direction = current_signal.get('direction', 'UNKNOWN').upper()
        current_confidence = current_signal.get('confidence', 50.0)
        
        # Simple similarity check based on direction and confidence range
        for loss_trade in recent_losses:
            similarity_score = 0.0
            matching_factors = []
            
            # Direction match
            if loss_trade.direction == current_direction:
                similarity_score += 0.4
                matching_factors.append('Direction')
            
            # Confidence range match (within 10%)
            if abs(loss_trade.confidence - current_confidence) <= 10:
                similarity_score += 0.3
                matching_factors.append('Confidence')
            
            # Market regime match (if available)
            current_regime = market_context.get('regime', {}).get('regime_type', '')
            if current_regime and loss_trade.market_conditions.get('regime') == current_regime:
                similarity_score += 0.3
                matching_factors.append('Market Regime')
            
            # If similarity is high enough, return warning
            if similarity_score >= similarity_threshold:
                return {
                    'similarity_score': similarity_score,
                    'past_loss_pct': loss_trade.profit_loss_pct,
                    'past_timestamp': loss_trade.entry_time.isoformat(),
                    'matching_factors': matching_factors,
                    'recommendation': (
                        f"⚠️ Similar setup to past losing trade ({loss_trade.profit_loss_pct:.2f}% loss). "
                        f"Exercise caution or reduce position size."
                    )
                }
        
        return None
    
    def get_recent_performance_summary(self, last_n_trades: int = 10) -> Dict[str, Any]:
        """Get summary of recent trading performance.
        
        Args:
            last_n_trades: Number of recent trades to analyze
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.trade_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'avg_loss': 0.0,
                'total_pnl': 0.0
            }
        
        recent_trades = self.trade_history[-last_n_trades:]
        winning_trades = [t for t in recent_trades if t.profit_loss_pct > 0]
        losing_trades = [t for t in recent_trades if t.profit_loss_pct < 0]
        
        total_trades = len(recent_trades)
        wins = len(winning_trades)
        losses = len(losing_trades)
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        avg_profit = sum(t.profit_loss_pct for t in winning_trades) / wins if wins > 0 else 0.0
        avg_loss = sum(t.profit_loss_pct for t in losing_trades) / losses if losses > 0 else 0.0
        total_pnl = sum(t.profit_loss_pct for t in recent_trades)
        
        return {
            'total_trades': total_trades,
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'total_pnl': total_pnl
        }

