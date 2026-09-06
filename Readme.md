# Data Extraction & Secure Validation Assignment

## Overview
This repository contains a Python solution designed to securely extract and validate structured entities from raw text feeds. Exactly four specific data types are targeted for extraction:

1. **Email Addresses** (including strict domain filtering for official ALU domain scopes)
2. **Credit Card Numbers** (validated with Luhn algorithm and masked for PCI compliance)
3. **Phone Numbers** (extracting standard local and international phone formats)
4. **HTML Tags** (extracting inline markup elements)

## Required Repository Structure

```text
alu-regex-data-extraction_{GithubUsername}/
├── input/
│   └── raw-text.txt          # Raw text data source
├── src/
│   └── main.py              # Extraction engine & validation script
├── output/
│   └── sample-output.json    # JSON output file
└── README.md                 # Project documentation