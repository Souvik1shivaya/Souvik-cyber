
import phonenumbers
from phonenumbers import geocoder, carrier, PhoneNumberFormat


def analyze_phone_number():
    print("=" * 45)
    print("       PHONE NUMBER OSINT TOOL")
    print("=" * 45)

    phone = input("\nEnter phone number with country code: ").strip()

    try:
        number = phonenumbers.parse(phone, None)

        print("\n[+] Analysis Result")
        print("-" * 45)

        print("International Format:",
              phonenumbers.format_number(
                  number, PhoneNumberFormat.INTERNATIONAL
              ))

        print("Country Code:", number.country_code)

        print("Possible Number:",
              phonenumbers.is_possible_number(number))

        print("Valid Number:",
              phonenumbers.is_valid_number(number))

        print("Region:",
              geocoder.description_for_number(number, "en") or "Unknown")

        print("Carrier:",
              carrier.name_for_number(number, "en") or "Unknown")

        print("-" * 45)
        print("Note: Region is numbering metadata,")
        print("not the person's current physical location.")

    except phonenumbers.NumberParseException as error:
        print("\n[!] Invalid phone number format.")
        print("Error:", error)


if __name__ == "__main__":
    analyze_phone_number()
