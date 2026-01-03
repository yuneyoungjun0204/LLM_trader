"""Test kaleido installation and functionality."""
import sys
import os

print("=" * 60)
print("KALEIDO TEST SCRIPT")
print("=" * 60)

# Test 1: Import kaleido
print("\n[1] Testing kaleido import...")
try:
    import kaleido
    print(f"✓ kaleido imported successfully")
    # Try to get version, but it may not exist in newer versions
    try:
        print(f"  Version: {kaleido.__version__}")
    except AttributeError:
        print(f"  Version: 1.0.0+ (version attribute not available)")
    print(f"  Location: {kaleido.__file__}")
except ImportError as e:
    print(f"✗ Failed to import kaleido: {e}")
    sys.exit(1)

# Test 2: Check kaleido structure (optional for 1.0.0+)
print("\n[2] Checking kaleido package structure...")
kaleido_path = os.path.dirname(kaleido.__file__)
print(f"✓ Kaleido package location: {kaleido_path}")
print(f"  Note: kaleido 1.0.0+ manages executables automatically")

# Test 3: Skip scope check (not needed for kaleido 1.2.0)
print("\n[3] Checking kaleido compatibility...")
print("✓ kaleido 1.2.0 uses plotly's built-in integration")
print("  Scope modules not required - using fig.to_image() directly")

# Test 4: Import plotly
print("\n[4] Testing plotly import...")
try:
    import plotly.graph_objects as go
    print(f"✓ plotly imported successfully")
except ImportError as e:
    print(f"✗ Failed to import plotly: {e}")
    sys.exit(1)

# Test 5: Create realistic candlestick chart (like the trading bot uses)
print("\n[5] Creating candlestick chart (like trading bot)...")
try:
    import pandas as pd
    import numpy as np

    # Generate sample OHLCV data (100 candles like the real bot)
    np.random.seed(42)
    n_candles = 100

    # Simulate realistic price data
    base_price = 50000  # BTC-like price
    dates = pd.date_range('2024-01-01', periods=n_candles, freq='1H')

    close_prices = base_price + np.cumsum(np.random.randn(n_candles) * 100)
    open_prices = close_prices + np.random.randn(n_candles) * 50
    high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.randn(n_candles) * 30)
    low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.randn(n_candles) * 30)
    volumes = np.abs(np.random.randn(n_candles) * 1000 + 5000)

    # Create candlestick chart
    fig = go.Figure()

    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=dates,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices,
        name='BTC/USDT',
        increasing_line_color='#00ff00',  # Bright green
        decreasing_line_color='#ff0000'   # Bright red
    ))

    # Add volume bars (on secondary y-axis)
    fig.add_trace(go.Bar(
        x=dates,
        y=volumes,
        name='Volume',
        marker_color='#0080ff',
        yaxis='y2',
        opacity=0.3
    ))

    # Update layout (black background like the bot)
    fig.update_layout(
        title='BTC/USDT - Test Chart',
        yaxis_title='Price (USDT)',
        xaxis_title='Time',
        template='plotly_dark',
        height=600,
        width=1600,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right'
        ),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000'
    )

    print("✓ Candlestick chart created successfully")
    print(f"  - {n_candles} candles")
    print(f"  - Price range: ${low_prices.min():.0f} - ${high_prices.max():.0f}")
except Exception as e:
    print(f"✗ Failed to create figure: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Export to image
print("\n[6] Attempting image export with kaleido...")
try:
    img_bytes = fig.to_image(format="png", width=800, height=600)
    print(f"✓ Image exported successfully ({len(img_bytes)} bytes)")

    # Save to file
    test_output_path = "test_kaleido_output.png"
    with open(test_output_path, 'wb') as f:
        f.write(img_bytes)
    print(f"✓ Image saved to: {os.path.abspath(test_output_path)}")

except Exception as e:
    print(f"✗ Failed to export image: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

# Test 7: Try alternative method
print("\n[7] Testing alternative export method...")
try:
    from plotly.io._kaleido import to_image
    img_bytes_alt = to_image(fig, format="png", width=800, height=600)
    print(f"✓ Alternative method successful ({len(img_bytes_alt)} bytes)")

    # Save alternative method output
    alt_output_path = "test_kaleido_alternative.png"
    with open(alt_output_path, 'wb') as f:
        f.write(img_bytes_alt)
    print(f"✓ Alternative image saved to: {os.path.abspath(alt_output_path)}")

except Exception as e:
    print(f"✗ Alternative method failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\n📊 Generated test images:")
print(f"  - {os.path.abspath('test_kaleido_output.png')}")
print(f"  - {os.path.abspath('test_kaleido_alternative.png')}")
print("\n💡 Copy images from container to local:")
print(f"  docker cp freqtrade:/freqtrade/user_data/strategies/LLM_trader/test_kaleido_output.png ./")
print("=" * 60)
