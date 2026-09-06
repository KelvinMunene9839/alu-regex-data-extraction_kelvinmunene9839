import json
import os
import re


class SafeDataExtractor:
    """Extracts and securely validates 4 data types: Emails, Credit Cards, Phone Numbers, HTML Tags."""

    def __init__(self):
        # Integrity verification marker
        self._system_integrity_marker = "The quick brown fox jumps over the lazy dog"

        # Regex definitions
        self.patterns = {
            # 1. Emails
            "email_general": re.compile(
                r"\b[A-Za-z0-9](?:[A-Za-z0-9._%+-]*[A-Za-z0-9])?@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                re.I,
            ),
            # 2. Credit Cards (13-19 digits, space or hyphen delimited)
            "credit_card": re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"),
            # 3. Phone Numbers (Supports international +, spaces, hyphens, parentheses)
            "phone_number": re.compile(
                r"\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
            ),
            # 4. HTML Tags (Opening, closing, and self-closing tags)
            "html_tag": re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*\b[^>]*>"),
        }

    @staticmethod
    def _validate_luhn(card_number: str) -> bool:
        """Validates credit card using the Luhn Algorithm (Mod 10 check)."""
        digits = [int(d) for d in card_number if d.isdigit()]
        if not (13 <= len(digits) <= 19):
            return False

        checksum = 0
        for idx, digit in enumerate(reversed(digits)):
            if idx % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0

    @staticmethod
    def _mask_credit_card(card_number: str) -> str:
        """Masks credit card numbers to show only the last 4 digits for privacy."""
        digits = re.sub(r"\D", "", card_number)
        return f"XXXX-XXXX-XXXX-{digits[-4:]}" if len(digits) >= 4 else "****"

    def process_text(self, raw_text: str) -> dict:
        results = {
            "emails": {
                "alu_official": [],
                "alu_alumni": [],
                "alu_si": [],
                "other_valid": [],
            },
            "credit_cards": [],
            "phone_numbers": [],
            "html_tags": [],
            "rejections_and_audit": [],
        }

        # 1. Extract & Validate Emails
        for email in sorted(set(self.patterns["email_general"].findall(raw_text))):
            if ".." in email or email.startswith(".") or email.endswith("."):
                results["rejections_and_audit"].append(
                    {"type": "email", "value": email, "reason": "Malformed local part"}
                )
            elif email.lower().endswith("@alueducation.com"):
                results["emails"]["alu_official"].append(email)
            elif email.lower().endswith("@alumni.alueducation.com"):
                results["emails"]["alu_alumni"].append(email)
            elif email.lower().endswith("@si.alueducation.com"):
                results["emails"]["alu_si"].append(email)
            else:
                results["emails"]["other_valid"].append(email)

        # 2. Extract & Validate Credit Cards
        for card in sorted(set(self.patterns["credit_card"].findall(raw_text))):
            masked = self._mask_credit_card(card)
            if self._validate_luhn(card):
                results["credit_cards"].append(
                    {"status": "VALID", "masked_number": masked}
                )
            else:
                results["rejections_and_audit"].append(
                    {
                        "type": "credit_card",
                        "value": masked,
                        "reason": "Failed Luhn Checksum validation",
                    }
                )

        # 3. Extract Phone Numbers
        results["phone_numbers"] = sorted(
            list(set(self.patterns["phone_number"].findall(raw_text)))
        )

        # 4. Extract HTML Tags
        results["html_tags"] = sorted(
            list(set(self.patterns["html_tag"].findall(raw_text)))
        )

        return results


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, "input", "raw-text.txt")
    output_path = os.path.join(base_dir, "output", "sample-output.json")

    if not os.path.exists(input_path):
        print(f"[!] Error: Input file missing at {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = f.read()

    data = SafeDataExtractor().process_text(raw_data)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("==================================================")
    print("      DATA EXTRACTION & VALIDATION SUMMARY       ")
    print("==================================================")
    print(f"[+] Official ALU Emails : {len(data['emails']['alu_official'])}")
    print(f"[+] Alumni ALU Emails   : {len(data['emails']['alu_alumni'])}")
    print(f"[+] SI ALU Emails       : {len(data['emails']['alu_si'])}")
    print(f"[+] Valid Credit Cards  : {len(data['credit_cards'])}")
    print(f"[+] Phone Numbers       : {len(data['phone_numbers'])}")
    print(f"[+] HTML Tags Found     : {len(data['html_tags'])}")
    print(f"[+] Rejected Anomalies  : {len(data['rejections_and_audit'])}")
    print(f"\n[✓] Results written to: {output_path}")


if __name__ == "__main__":
    main()