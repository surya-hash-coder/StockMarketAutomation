import subprocess
import sys
from pathlib import Path
from datetime import datetime


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

SRC_DIR = BASE_DIR / "src"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# LOG FILE
# ==========================================================

timestamp = datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S"
)

LOG_FILE = (
    LOG_DIR /
    f"pipeline_{timestamp}.log"
)


# ==========================================================
# PIPELINE STEPS
# ==========================================================

STEPS = [

    (
        "MARKET DATA COLLECTION",
        SRC_DIR / "collector.py"
    ),

    (
        "DATA CLEANING",
        SRC_DIR / "cleaner.py"
    ),

    (
        "TECHNICAL ANALYTICS V4",
        SRC_DIR / "analytics.py"
    ),

    (
        "DATABASE UPDATE V4",
        SRC_DIR / "database.py"
    ),

]


# ==========================================================
# LOGGER
# ==========================================================

def log(message):

    print(message)

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            message + "\n"
        )


# ==========================================================
# RUN SCRIPT
# ==========================================================

def run_step(name, script):

    log("")
    log("=" * 60)
    log(name)
    log("=" * 60)
    log("")

    if not script.exists():

        log(
            f"ERROR: Script not found: {script}"
        )

        return False

    try:

        result = subprocess.run(
            [
                sys.executable,
                str(script)
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        # ----------------------------------------------
        # SCRIPT OUTPUT
        # ----------------------------------------------

        if result.stdout:

            log(
                result.stdout.rstrip()
            )

        if result.stderr:

            log(
                result.stderr.rstrip()
            )

        # ----------------------------------------------
        # CHECK RESULT
        # ----------------------------------------------

        if result.returncode != 0:

            log("")
            log(
                f"❌ {name} FAILED"
            )

            log(
                f"Exit code: {result.returncode}"
            )

            return False

        log("")
        log(
            f"✓ {name} COMPLETE"
        )

        return True

    except Exception as error:

        log("")
        log(
            f"❌ ERROR running {name}"
        )

        log(
            str(error)
        )

        return False


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def main():

    start_time = datetime.now()

    log("")
    log("=" * 60)
    log("STOCK MARKET INTELLIGENCE PIPELINE")
    log("=" * 60)
    log(
        f"Started: {start_time}"
    )
    log(
        f"Python: {sys.executable}"
    )
    log("")

    # ----------------------------------------------
    # RUN PIPELINE
    # ----------------------------------------------

    for name, script in STEPS:

        success = run_step(
            name,
            script
        )

        if not success:

            log("")
            log("=" * 60)
            log("PIPELINE FAILED")
            log("=" * 60)
            log(
                f"Log file: {LOG_FILE}"
            )

            sys.exit(1)

    # ----------------------------------------------
    # COMPLETE
    # ----------------------------------------------

    end_time = datetime.now()

    duration = (
        end_time - start_time
    )

    log("")
    log("=" * 60)
    log("PIPELINE COMPLETE")
    log("=" * 60)

    log(
        f"Started: {start_time}"
    )

    log(
        f"Finished: {end_time}"
    )

    log(
        f"Duration: {duration}"
    )

    log(
        f"Log file: {LOG_FILE}"
    )

    log("")
    log(
        "✓ Market data collected"
    )

    log(
        "✓ Data cleaned"
    )

    log(
        "✓ Technical analytics calculated"
    )

    log(
        "✓ SQLite database updated"
    )

    log("")
    log(
        "STOCK MARKET INTELLIGENCE READY"
    )


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    main()
