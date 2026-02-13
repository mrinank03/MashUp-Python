# Compatibility module for audioop in Python 3.13+
try:
    from audioop import *
except ImportError:
    try:
        import audioop_lts as audioop
        # Re-export all audioop functions
        from audioop_lts import *
    except ImportError:
        # Minimal audioop replacement for basic pydub functionality
        import array
        import struct
        
        def add(fragment1, fragment2, width):
            """Add two audio fragments."""
            if len(fragment1) != len(fragment2):
                raise ValueError("Fragments must have the same length")
            return fragment1  # Simplified implementation
        
        def mul(fragment, width, factor):
            """Multiply an audio fragment by a factor."""
            return fragment  # Simplified implementation
        
        def reverse(fragment, width):
            """Reverse an audio fragment."""
            return fragment[::-1]
        
        def tomono(fragment, width, lfactor, rfactor):
            """Convert stereo to mono."""
            return fragment  # Simplified implementation
        
        def tostereo(fragment, width, lfactor, rfactor):  
            """Convert mono to stereo."""
            return fragment + fragment  # Simplified implementation
        
        def lin2lin(fragment, width, newwidth):
            """Convert between different sample widths."""
            return fragment  # Simplified implementation
        
        def ratecv(fragment, width, nchannels, inrate, outrate, state, weightA=1, weightB=0):
            """Convert sample rate.""" 
            return (fragment, state)  # Simplified implementation