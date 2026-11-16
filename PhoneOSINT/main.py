
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from datetime import datetime, timezone as utc_timezone
from pathlib import Path
import json
import re
import uuid

from config import APP_NAME, DEFAULT_REGION, REPORT_FILE
from public_search import PublicSearch


APP_VERSION = "3.0"
REPORT_SCHEMA_VERSION = "1.0"


def validate_phone_input(phone):

    if not phone:
        print("[!] Phone number cannot be empty.")
        return False

    if phone.count("+") > 1:
        print("[!] Multiple '+' symbols are not allowed.")
        return False

    if "+" in phone and not phone.startswith("+"):
        print("[!] '+' must be at the beginning.")
        return False

    if not re.fullmatch(r"\+?[0-9\s()-]+", phone):
        print("[!] Invalid characters in phone number.")
        return False

    digits = re.sub(r"\D", "", phone)

    if not 7 <= len(digits) <= 15:
        print("[!] Phone number must contain 7 to 15 digits.")
        return False

    return True


def analyze_phone(phone):

    try:
        number = phonenumbers.parse(phone, DEFAULT_REGION)

        if not phonenumbers.is_possible_number(number):
            print("[!] Number length is not possible.")
            return None

        if not phonenumbers.is_valid_number(number):
            print("[!] Number is not valid.")
            return None

        return {
            "phone_number": phonenumbers.format_number(
                number,
                phonenumbers.PhoneNumberFormat.E164
            ),
            "country": geocoder.description_for_number(
                number, "en"
            ),
            "carrier_metadata": carrier.name_for_number(
                number, "en"
            ),
            "timezones": list(
                timezone.time_zones_for_number(number)
            ),
            "country_code": number.country_code,
            "valid": True,
            "analysis_time_utc": datetime.now(
                utc_timezone.utc
            ).isoformat(),
            "location_note": (
                "Numbering metadata only; not live GPS."
            )
        }

    except phonenumbers.NumberParseException as error:
        print("[!] Number parsing error:", error)
        return None

    except Exception as error:
        print("[!] Unexpected analysis error:", error)
        return None


def create_report(analysis, links):

    timestamp = datetime.now(utc_timezone.utc).isoformat()

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "investigation_id": str(uuid.uuid4()),
        "created_at_utc": timestamp,

        "analysis": analysis,

        "search_metadata": {
            "search_timestamp_utc": timestamp,
            "total_search_categories": len(links),
            "search_categories": list(links.keys()),
            "verification_status": "Not verified",
            "search_method": "Public search engine URLs"
        },

        "public_search_links": links,

        "limitations": {
            "live_gps": (
                "Not available from a phone number alone."
            ),
            "ownership": (
                "Number validation does not identify the owner."
            ),
            "carrier": (
                "Carrier metadata may be outdated due to "
                "number portability."
            ),
            "social_media": (
                "Search links do not confirm account ownership."
            )
        }
    }


def validate_report(report):

    required_fields = [
        "application",
        "version",
        "report_schema_version",
        "investigation_id",
        "created_at_utc",
        "analysis",
        "search_metadata",
        "public_search_links",
        "limitations"
    ]

    missing = [
        field for field in required_fields
        if field not in report
    ]

    if missing:
        raise ValueError(
            "Missing report fields: " + ", ".join(missing)
        )

    if not isinstance(report["public_search_links"], dict):
        raise ValueError("Invalid public search links.")

    if not isinstance(report["analysis"], dict):
        raise ValueError("Invalid analysis data.")

    return True


def save_report(data):

    try:
        validate_report(data)

        report_path = Path(REPORT_FILE)

        with report_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"\n[+] Report saved: {report_path.resolve()}")
        return True

    except (OSError, ValueError, TypeError) as error:
        print("[!] Could not save report:", error)
        return False


def main():

    print("=" * 48)
    print(f"{APP_NAME} v{APP_VERSION}")
    print("Authorized Public Metadata Analysis")
    print("=" * 48)

    phone = input(
        "\nEnter your own or authorized phone number: "
    ).strip()

    if not validate_phone_input(phone):
        return

    analysis = analyze_phone(phone)

    if analysis is None:
        return

    try:
        search = PublicSearch(analysis["phone_number"])
        links = search.generate_search_links()

    except (ValueError, TypeError) as error:
        print("[!] Search module error:", error)
        return

    report = create_report(analysis, links)

    print("\n===== PHONE ANALYSIS =====")

    for key, value in analysis.items():
        print(f"{key}: {value}")

    print("\n===== PUBLIC SEARCH LINKS =====")

    for name, url in links.items():
        print(f"\n{name}:")
        print(url)

    print("\n===== INVESTIGATION DETAILS =====")
    print("Investigation ID:", report["investigation_id"])
    print("Application Version:", APP_VERSION)
    print("Report Schema:", REPORT_SCHEMA_VERSION)

    save_report(report)

    print("\n[+] Analysis completed.")
    print("[!] Use only your own or explicitly authorized number.")


if __name__ == "__main__":
    main()
