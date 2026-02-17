"""
Compatibility module for audioop in Python 3.13+
Provides audioop functionality for pydub compatibility
"""

# Try to import native audioop first (Python < 3.13)
try:
    import audioop  # type: ignore
    # Re-export all functions
    add = audioop.add  # type: ignore
    mul = audioop.mul  # type: ignore
    reverse = audioop.reverse  # type: ignore
    tomono = audioop.tomono  # type: ignore
    tostereo = audioop.tostereo  # type: ignore
    lin2lin = audioop.lin2lin  # type: ignore
    ratecv = audioop.ratecv  # type: ignore
    
except ImportError:
    # Try audioop-lts package (recommended for Python 3.13+)
    try:
        import audioop_lts  # type: ignore
        add = audioop_lts.add  # type: ignore
        mul = audioop_lts.mul  # type: ignore
        reverse = audioop_lts.reverse  # type: ignore
        tomono = audioop_lts.tomono  # type: ignore
        tostereo = audioop_lts.tostereo  # type: ignore
        lin2lin = audioop_lts.lin2lin  # type: ignore
        ratecv = audioop_lts.ratecv  # type: ignore
        
    except ImportError:
        # Fallback: Minimal stub implementations for basic pydub functionality
        # These won't work for all operations but prevent import errors
        
        def add(fragment1, fragment2, width):  # type: ignore
            """Add two audio fragments (stub)."""
            return fragment1
        
        def mul(fragment, width, factor):  # type: ignore
            """Multiply audio fragment by factor (stub)."""
            return fragment
        
        def reverse(fragment, width):  # type: ignore
            """Reverse audio fragment (stub)."""
            return fragment[::-1]
        
        def tomono(fragment, width, lfactor, rfactor):  # type: ignore
            """Convert stereo to mono (stub)."""
            return fragment
        
        def tostereo(fragment, width, lfactor, rfactor):  # type: ignore
            """Convert mono to stereo (stub)."""
            return fragment + fragment
        
        def lin2lin(fragment, width, newwidth):  # type: ignore
            """Convert sample width (stub)."""
            return fragment
        
        def ratecv(fragment, width, nchannels, inrate, outrate, state, weightA=1, weightB=0):  # type: ignore
            """Convert sample rate (stub)."""
            return (fragment, state)

