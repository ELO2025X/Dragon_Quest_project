import wave
import math
import random
import struct
import os

def generate_wav(filename, duration, freq_func, volume=0.5):
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    
    path = os.path.join("src", "assets", "sfx", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with wave.open(path, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            freq = freq_func(t, duration)
            
            # Generate waveform
            if filename == "attack.wav":
                # White noise burst
                value = random.uniform(-1, 1) * (1 - t/duration) # Decay
            elif filename == "magic.wav":
                # Sine sweep
                value = math.sin(2 * math.pi * freq * t)
            elif filename == "text_blip.wav":
                # Square wave
                value = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif filename == "menu.wav":
                # Sine blip
                value = math.sin(2 * math.pi * freq * t)
            else:
                value = 0
                
            # Scale and clamp
            sample = int(value * volume * 32767)
            sample = max(-32768, min(32767, sample))
            
            wav_file.writeframes(struct.pack('<h', sample))
            
    print(f"Generated {filename}")

def main():
    # Attack: Noise burst
    generate_wav("attack.wav", 0.2, lambda t, d: 0, volume=0.4)
    
    # Magic: High pitch sweep down
    generate_wav("magic.wav", 0.5, lambda t, d: 880 - (t/d)*440, volume=0.3)
    
    # Text Blip: High pitch short square wave
    generate_wav("text_blip.wav", 0.05, lambda t, d: 440, volume=0.2)
    
    # Menu: Short high blip
    generate_wav("menu.wav", 0.1, lambda t, d: 660, volume=0.3)

if __name__ == "__main__":
    main()
