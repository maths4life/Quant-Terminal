"""Market session / trading-hours logic for the NSE."""
from datetime import datetime, time as dtime
import pytz

IST = pytz.timezone("Asia/Kolkata")

MARKET_OPEN = dtime(9, 15)
MARKET_CLOSE = dtime(15, 30)


def is_nse_open():
    """Returns (is_open: bool, status_str: str)."""
    now = datetime.now(IST)

    if now.weekday() >= 5:
        return False, "CLOSED · Weekend"

    t = now.time()
    if MARKET_OPEN <= t <= MARKET_CLOSE:
        return True, "OPEN"

    if t < MARKET_OPEN:
        opens_at = IST.localize(datetime.combine(now.date(), MARKET_OPEN))
        mins = int((opens_at - now).seconds / 60)
        return False, f"PRE-MARKET · Opens in {mins}m"

    return False, "CLOSED · After Hours"
