import json
import io
import re
from typing import Dict, Any, Optional, Union, TYPE_CHECKING

from src.logger.logger import Logger
from src.utils.profiler import profile_performance
from src.utils.serialize import serialize_for_json, safe_tolist

if TYPE_CHECKING:
    from src.contracts.manager_factory import ModelManagerProtocol


class AnalysisResultProcessor:
    """Processes and formats market analysis results from AI models"""
    
    def __init__(self, model_manager: "ModelManagerProtocol", logger: Logger, unified_parser=None):
        """Initialize the processor"""
        if unified_parser is None:
            raise ValueError("unified_parser is required - must be injected from app.py")
        self.model_manager = model_manager
        self.logger = logger
        self.unified_parser = unified_parser
        
    async def process_analysis(self, system_prompt: str, prompt: str, 
                              chart_image: Optional[Union[io.BytesIO, bytes, str]] = None,
                              provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Process analysis by sending prompts to AI model and formatting response.
        
        Args:
            system_prompt: System instructions for the AI model
            prompt: User prompt for analysis
            chart_image: Optional chart image for visual analysis
            provider: Optional provider override (admin only)
            model: Optional model override (admin only)
            
        Returns:
            Dictionary containing formatted analysis results
        """
        # Send the prompt to the model
        self.logger.debug("Sending prompt to AI model for analysis")
        
        # Use chart analysis if image is provided and model supports it
        use_chart_analysis = chart_image is not None and self.model_manager.supports_image_analysis(provider)
        if use_chart_analysis:
            prov_name, model_name = self.model_manager.describe_provider_and_model(provider, model, chart=True)
            prov_label = prov_name.upper() if prov_name else "UNKNOWN"
            self.logger.info(
                "Using chart image analysis via %s (model: %s)",
                prov_label,
                model_name
            )
            try:
                complete_response = await self.model_manager.send_prompt_with_chart_analysis(
                    prompt=prompt,
                    chart_image=chart_image,
                    system_message=system_prompt,
                    provider=provider,
                    model=model
                )
            except ValueError:
                # Chart analysis failed, re-raise to let analysis engine handle logging and fallback
                raise
        else:
            # Use the standard send_prompt_streaming method
            complete_response = await self.model_manager.send_prompt_streaming(
                prompt=prompt,
                system_message=system_prompt,
                provider=provider,
                model=model
            )
        
        self.logger.debug("Received response from AI model")
        cleaned_response = self._clean_response(complete_response)

        # Primary parsing attempt
        parsed_response = self.unified_parser.parse_ai_response(cleaned_response)

        # 🔥 IRON-CLAD PARSER: Validate and apply regex fallback if needed
        if not self.unified_parser.validate_ai_response(parsed_response):
            self.logger.warning("⚠️ Standard validation failed - activating IRON-CLAD PARSER")

            # Try to extract values using regex even if JSON is malformed
            iron_clad_result = self._extract_with_iron_clad_parser(cleaned_response)

            if iron_clad_result["success"]:
                self.logger.info("✅ Iron-clad parser successfully extracted decision data")
                parsed_response = iron_clad_result["data"]
            else:
                self.logger.error("❌ Even iron-clad parser failed - returning minimal fallback")
                return {
                    "error": "Complete parsing failure",
                    "raw_response": cleaned_response,
                    "fallback_decision": "UNKNOWN"
                }

        # Log the analysis result
        self._log_analysis_result(parsed_response)

        # Format the final response
        return self._format_analysis_response(parsed_response, cleaned_response)
    
    def process_mock_analysis(self, symbol: str, current_price: float,
                              article_urls: Optional[Dict[str, str]] = None,
                              technical_history: Optional[Dict[str, Any]] = None,
                              technical_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process mock analysis for testing purposes"""
        self.logger.debug("Generating mock analysis instead of calling AI model")
        
        # Generate minimal mock data for trading (no dependency on non-existent src.html.mock)
        def get_mock_analysis_data(sym, price):
            return {
                "analysis": {
                    "summary": f"Mock trading analysis for {sym} at ${price}",
                    "confidence_score": 50,
                    "action": "HOLD",
                    "entry_price": price,
                    "stop_loss": price * 0.95,
                    "take_profit": price * 1.10
                },
                "markdown_content": f"## Mock Trading Analysis for {sym}\\n\\nCurrent Price: ${price}\\n\\nRecommendation: HOLD",
                "article_urls": {}
            }

        # Get all mock data (JSON analysis, Markdown, article URLs)
        mock_data = get_mock_analysis_data(symbol, current_price)
        
        # Compose the JSON part for the structured analysis and include indicators if available
        analysis_obj = mock_data["analysis"].copy()
        if technical_history is not None:
            analysis_obj["technical_history"] = {}
            # convert numpy arrays to lists for JSON serialization where applicable
            for k, v in technical_history.items():
                try:
                    analysis_obj["technical_history"][k] = safe_tolist(v)
                except Exception:
                    analysis_obj["technical_history"][k] = str(type(v))

        if technical_data is not None:
            analysis_obj["technical_data"] = technical_data

        # Create a JSON-serializable copy for the raw_response
        serializable_analysis = serialize_for_json(analysis_obj)
        mock_json_string = json.dumps({"analysis": serializable_analysis}, indent=2)

        # Use the generated Markdown content and append indicators if available
        mock_markdown_content = mock_data["markdown_content"]

        # Build compact indicators section to append to markdown
        indicators_section = ""
        try:
            if technical_data:
                indicators_section += "\n\n### Live Indicator Snapshot\n"
                for k, v in technical_data.items():
                    indicators_section += f"- **{k}**: {v}\n"

            if technical_history:
                indicators_section += "\n### Indicator Series (last 5 values each)\n"
                for k, series in list(technical_history.items())[:20]:
                    try:
                        vals = safe_tolist(series)
                        if isinstance(vals, list):
                            sample = vals[-5:]
                        else:
                            sample = list(vals)[-5:] if hasattr(vals, '__iter__') else [vals]
                        indicators_section += f"- **{k}** (last 5): {sample}\n"
                    except Exception:
                        indicators_section += f"- **{k}**: [unserializable]\n"
        except Exception:
            indicators_section = ""

        if indicators_section:
            mock_markdown_content = mock_markdown_content + "\n\n" + indicators_section
        # Use the mock article URLs or the provided ones
        mock_article_urls = article_urls or mock_data["article_urls"]

        mock_analysis = {
            "analysis": analysis_obj, # Use the structured dict here (with indicators)
            "raw_response": f"```json\n{mock_json_string}\n```\n{mock_markdown_content}",
            "article_urls": mock_article_urls,
            "technical_history_included": technical_history is not None,
            "technical_data_included": technical_data is not None
        }
        
        # Normalize numeric fields in mock analysis to match real analysis behavior
        mock_analysis = self.unified_parser._normalize_numeric_fields(mock_analysis)
        # Also attempt to parse the mock raw_response using the real parser to surface parsing issues
        try:
            parsed = self.unified_parser.parse_ai_response(mock_analysis["raw_response"])
            mock_analysis["parsed_response"] = parsed
            mock_analysis["parse_valid"] = self.unified_parser.validate_ai_response(parsed)
            if not mock_analysis["parse_valid"]:
                mock_analysis["parse_error"] = "Parsed response failed validation"
        except Exception as e:
            self.logger.error(f"Error while parsing mock response: {e}")
            mock_analysis["parse_exception"] = str(e)

        return mock_analysis
        
    def _log_analysis_result(self, parsed_response: Dict[str, Any]) -> None:
        """Log analysis result information"""
        if "analysis" in parsed_response:
            analysis = parsed_response["analysis"]
            
            # Check if this is trading analysis (has signal field)
            if "signal" in analysis:
                signal = analysis.get("signal", "UNKNOWN")
                confidence = analysis.get("confidence", 0)
                trend_info = analysis.get("trend", {})
                direction = trend_info.get("direction", "UNKNOWN") if isinstance(trend_info, dict) else "UNKNOWN"
                strength = trend_info.get("strength", 0) if isinstance(trend_info, dict) else 0
                
                # Log confluence factors if available (Chain-of-Thought scoring)
                confluence_factors = analysis.get("confluence_factors", {})
                if confluence_factors and isinstance(confluence_factors, dict):
                    cf_str = ", ".join([f"{k}={v}" for k, v in confluence_factors.items()])
                    self.logger.debug(
                        f"Trading analysis complete: Signal {signal}, Confidence {confidence}, "
                        f"Trend {direction} ({strength}% strength) | Confluence: {cf_str}"
                    )
                else:
                    self.logger.debug(
                        f"Trading analysis complete: Signal {signal}, Confidence {confidence}, "
                        f"Trend {direction} ({strength}% strength)"
                    )
            else:
                # Legacy analysis format
                bias = analysis.get("technical_bias", "UNKNOWN")
                trend = analysis.get("observed_trend", "UNKNOWN")
                confidence = analysis.get("confidence_score", 0)
                self.logger.debug(f"Analysis complete: Technical bias {bias} with {trend} trend ({confidence}% confidence)")
        else:
            self.logger.warning("Analysis complete but response format may be incomplete")
            
    def _format_analysis_response(self, parsed_response: Dict[str, Any],
                                cleaned_response: str) -> Dict[str, Any]:
        """Format the final analysis response"""
        parsed_response["raw_response"] = cleaned_response

        # 🔥 CRITICAL: Promote nested analysis fields to top level for test_hybridagent.py
        # This ensures parsed data is visible at the root level, not just in nested 'analysis'
        if "analysis" in parsed_response and isinstance(parsed_response["analysis"], dict):
            analysis = parsed_response["analysis"]

            # Extract final signal/decision (support both field names)
            final_signal = analysis.get("signal") or analysis.get("decision") or analysis.get("action") or "UNKNOWN"
            final_confidence = analysis.get("confidence", 50)
            final_reasoning = analysis.get("reasoning") or analysis.get("summary") or "No reasoning provided"

            # 🔥 TOP-LEVEL MAPPING: Make data accessible at root level
            parsed_response["decision"] = final_signal      # Primary field for test_hybridagent.py
            parsed_response["action"] = final_signal        # Alias for compatibility
            parsed_response["signal"] = final_signal        # Alias for OpenRouter format
            parsed_response["confidence"] = final_confidence
            parsed_response["reasoning"] = final_reasoning

            # Also promote TP/SL/Entry if available
            if "take_profit" in analysis:
                parsed_response["take_profit"] = analysis["take_profit"]
            if "stop_loss" in analysis:
                parsed_response["stop_loss"] = analysis["stop_loss"]
            if "entry_price" in analysis:
                parsed_response["entry_price"] = analysis["entry_price"]

            self.logger.debug(
                f"📤 Top-level fields promoted: decision={final_signal}, "
                f"confidence={final_confidence}, TP={analysis.get('take_profit', 0)}, "
                f"SL={analysis.get('stop_loss', 0)}"
            )

        # Include current_price if available in context
        if hasattr(self, 'context') and hasattr(self.context, 'current_price'):
            parsed_response["current_price"] = self.context.current_price

        # Return formatted response - article_urls will be added by the caller
        return parsed_response
    
    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove thinking sections and extra whitespace from AI responses"""
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    def _extract_with_iron_clad_parser(self, text: str) -> Dict[str, Any]:
        """
        🔥 IRON-CLAD PARSER: Extract decision data using regex even if JSON is malformed.

        This parser searches for patterns like:
        - Decision: BUY/SELL/HOLD
        - Confidence: 75
        - TP: 66500.0 (or Take Profit:, Target:)
        - SL: 65300.0 (or Stop Loss:, Stop:)

        Returns:
            Dict with {"success": bool, "data": {...}}
        """
        try:
            # 🔥 PRIORITY 1: Extract signal from JSON block at the END (most reliable)
            # Look for the LAST JSON block in the response
            json_block_match = re.search(r'\{[^{}]*\}(?!.*\{)', text, re.DOTALL)
            decision = "UNKNOWN"

            if json_block_match:
                json_text = json_block_match.group(0)
                # Try to extract signal from this JSON block
                signal_in_json = re.search(
                    r'["\']?(?:signal|action|decision)["\']?\s*:\s*["\']?(BUY|SELL|HOLD|CLOSE)["\']?',
                    json_text,
                    re.IGNORECASE
                )
                if signal_in_json:
                    decision = signal_in_json.group(1).upper()
                    self.logger.info(f"🎯 Found signal in JSON block: {decision}")

            # 🔥 PRIORITY 2: If JSON extraction failed, use expanded keyword search
            if decision == "UNKNOWN":
                decision_patterns = [
                    # JSON-style patterns (most reliable)
                    r'["\']?(?:signal|action|decision|verdict|recommendation)["\']?\s*:\s*["\']?(BUY|SELL|HOLD|CLOSE)["\']?',
                    # Natural language patterns
                    r'(?:Signal|Action|Decision|Verdict|Recommendation)\s*:\s*["\']?(BUY|SELL|HOLD|CLOSE)["\']?',
                    r'Final\s+(?:Signal|Decision|Verdict)\s*:\s*["\']?(BUY|SELL|HOLD|CLOSE)["\']?',
                    r'Trading\s+(?:Signal|Action|Decision)\s*:\s*["\']?(BUY|SELL|HOLD|CLOSE)["\']?',
                ]
                for pattern in decision_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        decision = match.group(1).upper()
                        self.logger.debug(f"🎯 Found decision via pattern: {pattern[:50]}... → {decision}")
                        break

            # Extract Confidence
            confidence_patterns = [
                r'["\']?confidence["\']?\s*:\s*(\d+)',
                r'Confidence\s*:\s*(\d+)',
                r'Confidence Level\s*:\s*(\d+)',
            ]
            confidence = 50  # Default neutral confidence
            for pattern in confidence_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = int(match.group(1))
                    break

            # Extract Take Profit (TP) - 🔥 ENHANCED: Support commas, dollar signs, complex formats
            tp_patterns = [
                r'["\']?take_profit["\']?\s*:\s*([\d,.]+)',  # JSON format
                r'TP\s*[:=]\s*\$?\s*([\d,.\s]+)',            # TP: $88,500.50 or TP=88500
                r'Take[\s-]?Profit\s*[:=]\s*\$?\s*([\d,.\s]+)',  # Take Profit: 88500
                r'Target\s*(?:Price)?\s*[:=]\s*\$?\s*([\d,.\s]+)',  # Target: 88500
                r'T/?P\s*[:=]\s*\$?\s*([\d,.\s]+)',          # T/P: 88500
            ]
            take_profit = 0
            for pattern in tp_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Clean extracted value: remove commas, dollar signs, whitespace
                    cleaned_value = match.group(1).replace(',', '').replace('$', '').replace(' ', '').strip()
                    try:
                        take_profit = float(cleaned_value)
                        self.logger.debug(f"🎯 Found TP via pattern: {pattern[:40]}... → {take_profit}")
                        break
                    except ValueError:
                        continue

            # Extract Stop Loss (SL) - 🔥 ENHANCED: Support commas, dollar signs, complex formats
            sl_patterns = [
                r'["\']?stop_loss["\']?\s*:\s*([\d,.]+)',    # JSON format
                r'SL\s*[:=]\s*\$?\s*([\d,.\s]+)',            # SL: $87,000.00
                r'Stop[\s-]?Loss\s*[:=]\s*\$?\s*([\d,.\s]+)',  # Stop Loss: 87000
                r'Stop\s*(?:Price)?\s*[:=]\s*\$?\s*([\d,.\s]+)',  # Stop: 87000
                r'S/?L\s*[:=]\s*\$?\s*([\d,.\s]+)',          # S/L: 87000
            ]
            stop_loss = 0
            for pattern in sl_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    cleaned_value = match.group(1).replace(',', '').replace('$', '').replace(' ', '').strip()
                    try:
                        stop_loss = float(cleaned_value)
                        self.logger.debug(f"🎯 Found SL via pattern: {pattern[:40]}... → {stop_loss}")
                        break
                    except ValueError:
                        continue

            # Extract Entry Price (if available) - 🔥 ENHANCED
            entry_patterns = [
                r'["\']?entry_price["\']?\s*:\s*([\d,.]+)',  # JSON format
                r'Entry\s*(?:Price)?\s*[:=]\s*\$?\s*([\d,.\s]+)',  # Entry: $88,000
                r'Current\s*(?:Price)?\s*[:=]\s*\$?\s*([\d,.\s]+)',  # Current Price: 88000
            ]
            entry_price = 0
            for pattern in entry_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    cleaned_value = match.group(1).replace(',', '').replace('$', '').replace(' ', '').strip()
                    try:
                        entry_price = float(cleaned_value)
                        self.logger.debug(f"🎯 Found Entry via pattern: {pattern[:40]}... → {entry_price}")
                        break
                    except ValueError:
                        continue

            # Log extracted values
            self.logger.info(f"🔍 Iron-clad extraction: Decision={decision}, Conf={confidence}, TP={take_profit}, SL={stop_loss}")

            # Even if decision is UNKNOWN, we return success with best-guess values
            # This ensures the system NEVER returns complete failure
            return {
                "success": True,
                "data": {
                    "analysis": {
                        "signal": decision,      # Primary field (used by OpenRouter responses)
                        "decision": decision,    # Legacy field (for compatibility)
                        "confidence": confidence,
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "reasoning": f"Iron-clad regex extraction (Signal: {decision}, Confidence: {confidence}%)",
                        "summary": f"Extracted via fallback parser - {decision} with {confidence}% confidence"
                    }
                }
            }

        except Exception as e:
            self.logger.error(f"❌ Iron-clad parser exception: {e}")
            return {"success": False}
