"""
Ollama Connection Test Script

Tests connection to Ollama server and verifies all task-based models are available.
Run this script before starting the trading bot to ensure Ollama is properly configured.

Usage:
    python test_ollama.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.loader import config
from src.logger.logger import Logger
from src.platforms.ai_providers.ollama import OllamaClient


async def test_ollama_connection():
    """Test Ollama server connection and model availability."""

    # Initialize logger
    logger = Logger(debug=True)
    logger.info("=" * 60)
    logger.info("OLLAMA CONNECTION TEST")
    logger.info("=" * 60)

    # Get Ollama configuration
    ollama_url = config.OLLAMA_BASE_URL
    main_model = config.OLLAMA_MAIN_MODEL
    math_model = config.OLLAMA_MATH_MODEL
    reasoning_model = config.OLLAMA_REASONING_MODEL
    summary_model = config.OLLAMA_SUMMARY_MODEL

    logger.info(f"\nOllama Server: {ollama_url}")
    logger.info(f"Main Model: {main_model}")
    logger.info(f"Math Model: {math_model}")
    logger.info(f"Reasoning Model: {reasoning_model}")
    logger.info(f"Summary Model: {summary_model}")
    logger.info("-" * 60)

    # Create Ollama client
    async with OllamaClient(base_url=ollama_url, logger=logger) as client:

        # Test 1: Check server connectivity
        logger.info("\n[TEST 1] Checking Ollama server connectivity...")
        try:
            # Try a simple completion request with a small prompt
            test_messages = [{"role": "user", "content": "Hello"}]
            test_config = {"max_tokens": 10, "temperature": 0.7}

            response = await client.chat_completion(
                model=main_model,
                messages=test_messages,
                model_config=test_config
            )

            if response and "choices" in response:
                logger.info("✓ Ollama server is running and responding")
            else:
                logger.error("✗ Ollama server returned invalid response")
                logger.error(f"Response: {response}")
                return False

        except Exception as e:
            logger.error(f"✗ Failed to connect to Ollama server: {e}")
            logger.error(f"\nMake sure Ollama is running:")
            logger.error(f"  1. Install Ollama from https://ollama.com")
            logger.error(f"  2. Start Ollama server: ollama serve")
            logger.error(f"  3. Verify URL: {ollama_url}")
            return False

        # Test 2: Check model availability
        logger.info("\n[TEST 2] Checking model availability...")
        models_to_check = {
            "Main Analysis (Qwen2.5 14B)": main_model,
            "Technical Calc (Qwen2-Math 7B)": math_model,
            "Pattern Reasoning (DeepSeek-R1 7B)": reasoning_model,
            "News Summary (Llama 3.1 8B)": summary_model
        }

        all_models_available = True
        for model_name, model_id in models_to_check.items():
            is_available = await client.check_model_availability(model_id)
            if is_available:
                logger.info(f"✓ {model_name}: {model_id}")
            else:
                logger.warning(f"✗ {model_name}: {model_id} - NOT FOUND")
                logger.warning(f"  → Run: ollama pull {model_id}")
                all_models_available = False

        if not all_models_available:
            logger.warning("\n⚠ Some models are missing. Pull them using:")
            logger.warning(f"  ollama pull {main_model}")
            logger.warning(f"  ollama pull {math_model}")
            logger.warning(f"  ollama pull {reasoning_model}")
            logger.warning(f"  ollama pull {summary_model}")
            return False

        # Test 3: Test each model with a simple prompt
        logger.info("\n[TEST 3] Testing each model with sample prompts...")

        test_cases = [
            ("Main Analysis", main_model, "Analyze BTC price: $50000. Trend?", {"temperature": 0.3, "max_tokens": 50}),
            ("Math Calculation", math_model, "Calculate RSI: (gains=100, losses=80, period=14)", {"temperature": 0.1, "max_tokens": 50}),
            ("Pattern Reasoning", reasoning_model, "Pattern: Higher highs and higher lows. Trend?", {"temperature": 0.4, "max_tokens": 50}),
            ("News Summary", summary_model, "Summarize: Bitcoin hits new ATH today.", {"temperature": 0.7, "max_tokens": 50})
        ]

        for task_name, model_id, prompt, model_config in test_cases:
            try:
                logger.info(f"\n  Testing {task_name} ({model_id})...")
                messages = [{"role": "user", "content": prompt}]

                response = await client.chat_completion(
                    model=model_id,
                    messages=messages,
                    model_config=model_config
                )

                if response and "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    logger.info(f"  ✓ Response: {content[:100]}...")
                else:
                    logger.error(f"  ✗ Invalid response from {model_id}")
                    return False

            except Exception as e:
                logger.error(f"  ✗ Error testing {model_id}: {e}")
                return False

        # Test 4: Test streaming
        logger.info("\n[TEST 4] Testing streaming mode...")
        try:
            test_messages = [{"role": "user", "content": "Count to 5"}]
            test_config = {"max_tokens": 50, "temperature": 0.7}

            logger.info("  Starting stream...")
            response = await client.stream_chat_completion(
                model=main_model,
                messages=test_messages,
                model_config=test_config
            )

            if response and "choices" in response:
                logger.info("  ✓ Streaming mode works")
            else:
                logger.warning("  ✗ Streaming mode failed (optional feature)")

        except Exception as e:
            logger.warning(f"  ✗ Streaming test failed: {e} (optional feature)")

        # Success
        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("\nOllama is ready for trading bot usage.")
        logger.info("\nTask-based model mapping:")
        logger.info(f"  • main_analysis     → {main_model}")
        logger.info(f"  • technical_calc    → {math_model}")
        logger.info(f"  • pattern_reasoning → {reasoning_model}")
        logger.info(f"  • news_summary      → {summary_model}")
        logger.info("\nYou can now start the trading bot with:")
        logger.info("  python start.py")
        logger.info("=" * 60)

        return True


async def main():
    """Main entry point."""
    try:
        success = await test_ollama_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  OLLAMA CONNECTION TEST SCRIPT")
    print("=" * 60)
    print("\nThis script will verify:")
    print("  1. Ollama server is running")
    print("  2. All required models are installed")
    print("  3. Models respond correctly")
    print("  4. Streaming mode works")
    print("\n" + "=" * 60 + "\n")

    asyncio.run(main())
