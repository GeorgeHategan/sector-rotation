#!/usr/bin/env python3
"""
Run sector rotation scanner only during market hours
US Stock Market: 9:30 AM - 4:00 PM EST (Monday-Friday)
"""

from datetime import datetime
import pytz
import subprocess
import sys

def is_market_open():
    """
    Check if US stock market is currently open
    Returns: (bool, str) - (is_open, reason)
    """
    # Get current time in US Eastern timezone
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False, f"Market closed: Weekend ({now.strftime('%A')})"
    
    # Market hours: 9:30 AM - 4:00 PM EST
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if now < market_open_time:
        return False, f"Market not open yet (opens at 9:30 AM EST, currently {now.strftime('%I:%M %p EST')})"
    elif now > market_close_time:
        return False, f"Market closed (closed at 4:00 PM EST, currently {now.strftime('%I:%M %p EST')})"
    else:
        return True, f"Market is open (current time: {now.strftime('%I:%M %p EST')})"


def run_scanner():
    """Run the sector rotation scanner"""
    print("=" * 80)
    print("🚀 Starting Sector Rotation Scanner...")
    print("=" * 80)
    
    try:
        # Run the scanner
        result = subprocess.run(['python3', 'sector_rotation_scanner.py'], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("\n" + "=" * 80)
            print("✅ Scanner completed successfully!")
            print("=" * 80)
            return True
        else:
            print("\n" + "=" * 80)
            print("❌ Scanner failed!")
            print("=" * 80)
            return False
            
    except Exception as e:
        print(f"\n❌ Error running scanner: {e}")
        return False


def main():
    """Main function"""
    print("=" * 80)
    print("SECTOR ROTATION SCANNER - MARKET HOURS CHECK")
    print("=" * 80)
    
    is_open, reason = is_market_open()
    print(f"\n📊 Status: {reason}\n")
    
    if is_open:
        print("✅ Market is open - Running scanner...\n")
        success = run_scanner()
        sys.exit(0 if success else 1)
    else:
        print("⏰ Market is closed - Scanner will not run.")
        print("\nMarket Hours:")
        print("  Monday-Friday: 9:30 AM - 4:00 PM EST")
        print("  Closed: Weekends and US holidays")
        print("\nTo run anyway, use: python3 sector_rotation_scanner.py")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()
