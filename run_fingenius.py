#!/usr/bin/env python3
"""
Convenience script to run FinGenius with various options
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def check_venv():
    """Check if virtual environment is activated"""
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if not in_venv:
        print("⚠️  Virtual environment does not seem to be activated.")
        print("   Please activate it before running this script:")
        if os.name == 'nt':  # Windows
            print("   .venv\\Scripts\\activate")
        else:  # Unix/macOS
            print("   source .venv/bin/activate")
        print()
    
    return in_venv

def run_fingenius(stock_code, tts=False, debate_rounds=2, max_steps=3, output_format="text", output_file=None):
    """Run FinGenius with specified options"""
    # Check if main.py exists
    if not Path("main.py").exists():
        print("✗ main.py not found. Please run this script from the FinGenius directory.")
        return False
    
    # Build command
    cmd = ["python", "main.py", stock_code]
    
    if tts:
        cmd.append("--tts")
    
    if debate_rounds != 2:
        cmd.extend(["--debate-rounds", str(debate_rounds)])
    
    if max_steps != 3:
        cmd.extend(["--max-steps", str(max_steps)])
    
    if output_format != "text":
        cmd.extend(["--format", output_format])
    
    if output_file:
        cmd.extend(["--output", output_file])
    
    print(f"Running command: {' '.join(cmd)}")
    print()
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running FinGenius: {e}")
        return False
    except FileNotFoundError:
        print("✗ Python not found. Please make sure Python is installed and in your PATH.")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run FinGenius with various options")
    parser.add_argument("stock_code", help="Stock code to analyze (e.g., 000001)")
    parser.add_argument("--tts", action="store_true", help="Enable text-to-speech")
    parser.add_argument("--debate-rounds", type=int, default=2, help="Number of debate rounds (default: 2)")
    parser.add_argument("--max-steps", type=int, default=3, help="Maximum steps per agent (default: 3)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--check-venv", action="store_true", help="Check if virtual environment is activated")
    
    args = parser.parse_args()
    
    print("=== FinGenius Runner ===")
    print(f"Stock code: {args.stock_code}")
    print(f"TTS enabled: {args.tts}")
    print(f"Debate rounds: {args.debate_rounds}")
    print(f"Max steps: {args.max_steps}")
    print(f"Output format: {args.format}")
    if args.output:
        print(f"Output file: {args.output}")
    print()
    
    # Check virtual environment if requested
    if args.check_venv:
        check_venv()
    
    # Run FinGenius
    success = run_fingenius(
        stock_code=args.stock_code,
        tts=args.tts,
        debate_rounds=args.debate_rounds,
        max_steps=args.max_steps,
        output_format=args.format,
        output_file=args.output
    )
    
    if success:
        print("\n✓ FinGenius completed successfully!")
        return 0
    else:
        print("\n✗ FinGenius failed to complete.")
        return 1

if __name__ == "__main__":
    sys.exit(main())