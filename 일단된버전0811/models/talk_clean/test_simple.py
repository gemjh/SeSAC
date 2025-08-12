#!/usr/bin/env python3
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_simple.py <wav_file_path>")
        sys.exit(1)
    
    wav_path = sys.argv[1]
    print(f"Processing: {wav_path}")
    print("42")  # 임시 점수