"""
Trade Validator - Validates and corrects trade decisions to ensure logical consistency.
"""

from typing import Dict, Any, Tuple, Optional


class TradeValidator:
    """Validates trade decisions and provides auto-correction capabilities."""
    
    @staticmethod
    def validate_trade_decision(
        result: Dict[str, Any],
        current_price: float
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Validate a trade decision for logical consistency.
        
        Args:
            result: AI analysis result dictionary
            current_price: Current market price
        
        Returns:
            Tuple of (is_valid, error_message, corrected_result)
        """
        decision = result.get('decision', 'HOLD')
        direction = result.get('direction', 'NEUTRAL')
        entry_price = result.get('entry_price', current_price)
        stop_loss = result.get('stop_loss', 0)
        take_profit = result.get('take_profit', 0)
        
        # HOLD decisions are always valid
        if decision in ['HOLD', 'CLOSE']:
            return True, None, result
        
        # Must have direction
        if direction == 'NEUTRAL' and decision in ['BUY', 'SELL']:
            return False, "Missing direction for BUY/SELL decision", None
        
        # Must have SL and TP
        if stop_loss <= 0 or take_profit <= 0:
            return False, f"Invalid SL ({stop_loss}) or TP ({take_profit})", None
        
        # Validate LONG (BUY) trades
        if decision == 'BUY' or direction == 'LONG':
            if stop_loss >= entry_price:
                return False, f"LONG SL ({stop_loss}) must be < entry ({entry_price})", None
            if take_profit <= entry_price:
                return False, f"LONG TP ({take_profit}) must be > entry ({entry_price})", None
            
            # Check R/R ratio
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
            if risk <= 0 or reward <= 0:
                return False, f"Invalid risk/reward calculation (risk: {risk}, reward: {reward})", None
            
            rr_ratio = reward / risk if risk > 0 else 0
            if rr_ratio < 1.0:
                return False, f"R/R ratio ({rr_ratio:.2f}) < 1.0 (minimum required)", None
        
        # Validate SHORT (SELL) trades
        elif decision == 'SELL' or direction == 'SHORT':
            if stop_loss <= entry_price:
                return False, f"SHORT SL ({stop_loss}) must be > entry ({entry_price})", None
            if take_profit >= entry_price:
                return False, f"SHORT TP ({take_profit}) must be < entry ({entry_price})", None
            
            # Check R/R ratio
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
            if risk <= 0 or reward <= 0:
                return False, f"Invalid risk/reward calculation (risk: {risk}, reward: {reward})", None
            
            rr_ratio = reward / risk if risk > 0 else 0
            if rr_ratio < 1.0:
                return False, f"R/R ratio ({rr_ratio:.2f}) < 1.0 (minimum required)", None
        
        return True, None, result
    
    @staticmethod
    def auto_correct_direction(
        result: Dict[str, Any],
        current_price: float,
        default_rr_ratio: float = 1.5
    ) -> Dict[str, Any]:
        """Attempt to auto-correct swapped TP/SL values.
        
        Args:
            result: AI analysis result dictionary
            current_price: Current market price
            default_rr_ratio: Default risk/reward ratio for correction (default: 1.5)
        
        Returns:
            Corrected result dictionary
        """
        corrected = result.copy()
        decision = result.get('decision', 'HOLD')
        direction = result.get('direction', 'NEUTRAL')
        entry_price = result.get('entry_price', current_price)
        stop_loss = result.get('stop_loss', 0)
        take_profit = result.get('take_profit', 0)
        
        if decision not in ['BUY', 'SELL']:
            return corrected
        
        # Try to correct LONG trades
        if decision == 'BUY' or direction == 'LONG':
            # If SL > entry and TP < entry, they're swapped
            if stop_loss > entry_price and take_profit < entry_price:
                corrected['stop_loss'] = take_profit
                corrected['take_profit'] = stop_loss
            # If only SL is wrong, calculate based on TP
            elif stop_loss >= entry_price and take_profit > entry_price:
                risk = (take_profit - entry_price) / default_rr_ratio
                corrected['stop_loss'] = entry_price - risk
            # If only TP is wrong, calculate based on SL
            elif stop_loss < entry_price and take_profit <= entry_price:
                reward = (entry_price - stop_loss) * default_rr_ratio
                corrected['take_profit'] = entry_price + reward
        
        # Try to correct SHORT trades
        elif decision == 'SELL' or direction == 'SHORT':
            # If SL < entry and TP > entry, they're swapped
            if stop_loss < entry_price and take_profit > entry_price:
                corrected['stop_loss'] = take_profit
                corrected['take_profit'] = stop_loss
            # If only SL is wrong, calculate based on TP
            elif stop_loss <= entry_price and take_profit < entry_price:
                risk = (entry_price - take_profit) / default_rr_ratio
                corrected['stop_loss'] = entry_price + risk
            # If only TP is wrong, calculate based on SL
            elif stop_loss > entry_price and take_profit >= entry_price:
                reward = (stop_loss - entry_price) * default_rr_ratio
                corrected['take_profit'] = entry_price - reward
        
        return corrected
    
    @staticmethod
    def get_validation_report(
        result: Dict[str, Any],
        current_price: float
    ) -> str:
        """Generate a human-readable validation report.
        
        Args:
            result: AI analysis result dictionary
            current_price: Current market price
        
        Returns:
            Formatted validation report string
        """
        decision = result.get('decision', 'HOLD')
        direction = result.get('direction', 'NEUTRAL')
        entry_price = result.get('entry_price', current_price)
        stop_loss = result.get('stop_loss', 0)
        take_profit = result.get('take_profit', 0)
        confidence = result.get('confidence', 0)
        
        lines = [
            "=" * 60,
            "TRADE VALIDATION REPORT",
            "=" * 60,
            f"Decision: {decision}",
            f"Direction: {direction}",
            f"Confidence: {confidence}%",
            f"Entry Price: {entry_price:.4f}",
            f"Stop Loss: {stop_loss:.4f}",
            f"Take Profit: {take_profit:.4f}",
            ""
        ]
        
        # Validate
        is_valid, error_msg, _ = TradeValidator.validate_trade_decision(result, current_price)
        
        if is_valid:
            lines.append("✅ Validation: PASSED")
            
            # Calculate R/R
            if decision == 'BUY' or direction == 'LONG':
                risk = entry_price - stop_loss
                reward = take_profit - entry_price
                rr_ratio = reward / risk if risk > 0 else 0
            elif decision == 'SELL' or direction == 'SHORT':
                risk = stop_loss - entry_price
                reward = entry_price - take_profit
                rr_ratio = reward / risk if risk > 0 else 0
            else:
                rr_ratio = 0
                risk = 0
                reward = 0
            
            lines.extend([
                f"Risk: {risk:.4f} ({risk/entry_price*100:.2f}%)",
                f"Reward: {reward:.4f} ({reward/entry_price*100:.2f}%)",
                f"R/R Ratio: {rr_ratio:.2f}:1"
            ])
        else:
            lines.append(f"❌ Validation: FAILED")
            lines.append(f"Error: {error_msg}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)

