"""
Crypto Trading Bot - Entry Point
Automated trading with AI-powered decisions.
"""
import asyncio
import sys
import os
import argparse
from src.config.loader import config
from src.app import CryptoTradingBot
from src.logger.logger import Logger
import warnings

# Suppress SyntaxWarning from docopt libraries
warnings.filterwarnings("ignore", category=SyntaxWarning, module="docopt")

# Configure kaleido path explicitly for plotly image export
try:
    import kaleido
    # Get the kaleido package path
    kaleido_path = os.path.dirname(kaleido.__file__)

    # Try multiple possible executable locations (kaleido 0.2.1+ uses executable/bin/)
    possible_paths = [
        os.path.join(kaleido_path, 'executable', 'bin', 'kaleido.exe'),  # Windows (0.2.1+)
        os.path.join(kaleido_path, 'executable', 'bin', 'kaleido'),      # Unix (0.2.1+)
        os.path.join(kaleido_path, 'executable', 'kaleido.exe'),         # Windows (old)
        os.path.join(kaleido_path, 'executable', 'kaleido'),             # Unix (old)
    ]

    for kaleido_bin in possible_paths:
        if os.path.exists(kaleido_bin):
            os.environ['KALEIDO_EXECUTABLE_PATH'] = kaleido_bin
            break
except ImportError:
    pass  # kaleido not installed, will be handled by chart_generator

from src.utils.graceful_shutdown_manager import GracefulShutdownManager


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Crypto Trading Bot - AI-powered automated trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py                    # Trade default symbol from config
  python start.py ETH/USDT           # Trade ETH/USDT
  python start.py BTC/USDT -t 4h     # Trade BTC/USDT on 4h timeframe
  python start.py SOL/USDT -t 1h     # Trade SOL/USDT on 1h timeframe
        """
    )
    parser.add_argument(
        "symbol",
        nargs="?",
        default=None,
        help="Trading symbol (e.g., BTC/USDT). Default: from config"
    )
    parser.add_argument(
        "-t", "--timeframe",
        default=None,
        help="Timeframe for trading (e.g., 1h, 4h, 1d). Default: from config"
    )
    return parser.parse_args()


async def main_async():
    """Async entry point for the application"""
    args = parse_args()
    
    logger = Logger(logger_name="Bot", logger_debug=config.LOGGER_DEBUG)
    bot = CryptoTradingBot(logger, config)
    
    try:
        await bot.initialize()
        
        symbol = args.symbol or config.CRYPTO_PAIR
        timeframe = args.timeframe or config.TIMEFRAME
        
        logger.info(f"\n{'='*60}")
        logger.info("CRYPTO TRADING BOT")
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Timeframe: {timeframe}")
        logger.info("Press Ctrl+C to stop")
        logger.info(f"{'='*60}\n")
        
        await bot.run(symbol, timeframe)
    except asyncio.CancelledError:
        logger.info("Trading cancelled, shutting down...")
    finally:
        # Clean shutdown
        await bot.shutdown()


def main() -> None:
    """Main entry point with clean shutdown delegation."""
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    shutdown_manager = GracefulShutdownManager(loop)
    shutdown_manager.setup_signal_handlers()
    
    try:
        loop.run_until_complete(main_async())
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received - initiating graceful shutdown...")
        loop.run_until_complete(shutdown_manager.shutdown_gracefully())
    except Exception as e:
        print(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        loop.run_until_complete(shutdown_manager.shutdown_gracefully())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
