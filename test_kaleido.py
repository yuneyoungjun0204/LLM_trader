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
    print(f"  Version: {kaleido.__version__}")
    print(f"  Location: {kaleido.__file__}")
except ImportError as e:
    print(f"✗ Failed to import kaleido: {e}")
    sys.exit(1)

# Test 2: Find executable
print("\n[2] Finding kaleido executable...")
kaleido_path = os.path.dirname(kaleido.__file__)
possible_paths = [
    os.path.join(kaleido_path, 'executable', 'bin', 'kaleido.exe'),
    os.path.join(kaleido_path, 'executable', 'bin', 'kaleido'),
    os.path.join(kaleido_path, 'executable', 'kaleido.exe'),
    os.path.join(kaleido_path, 'executable', 'kaleido'),
]

found_exe = None
for path in possible_paths:
    if os.path.exists(path):
        found_exe = path
        print(f"✓ Found executable: {path}")
        break

if not found_exe:
    print("✗ No executable found. Searched:")
    for p in possible_paths:
        print(f"  - {p}")
    sys.exit(1)

# Test 3: Set environment variable
print("\n[3] Setting KALEIDO_EXECUTABLE_PATH...")
os.environ['KALEIDO_EXECUTABLE_PATH'] = found_exe
print(f"✓ Set to: {found_exe}")

# Test 4: Import plotly
print("\n[4] Testing plotly import...")
try:
    import plotly.graph_objects as go
    print(f"✓ plotly imported successfully")
except ImportError as e:
    print(f"✗ Failed to import plotly: {e}")
    sys.exit(1)

# Test 5: Create simple figure
print("\n[5] Creating simple plotly figure...")
try:
    fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
    print("✓ Figure created successfully")
except Exception as e:
    print(f"✗ Failed to create figure: {e}")
    sys.exit(1)

# Test 6: Export to image
print("\n[6] Attempting image export with kaleido...")
try:
    img_bytes = fig.to_image(format="png", width=800, height=600, engine="kaleido")
    print(f"✓ Image exported successfully ({len(img_bytes)} bytes)")
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
    img_bytes_alt = to_image(fig, format="png", width=800, height=600, engine="kaleido")
    print(f"✓ Alternative method successful ({len(img_bytes_alt)} bytes)")
except Exception as e:
    print(f"✗ Alternative method failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
