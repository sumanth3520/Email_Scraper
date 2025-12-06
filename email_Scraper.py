import re
import csv
import requests

# Match any email at a uga-related domain (uga.edu, cs.uga.edu, caes.uga.edu, etc.)
EMAIL_REGEX = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]*uga\.edu')

# Optional: skip obvious non-faculty addresses like web admins, generic info emails
SKIP_PREFIXES = (
    "web", "info", "help", "support", "admissions",
    "postmaster", "noreply", "no-reply", "abuse",
    "csci-web"
)


def looks_like_faculty_email(email: str) -> bool:
    local = email.split("@", 1)[0].lower()
    return not any(local.startswith(p) for p in SKIP_PREFIXES)


def scrape_faculty_page(url: str):
    """
    Fetch one faculty directory page and return a set of emails found on it.
    """
    print(f"\n[+] Fetching: {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    html = resp.text

    all_matches = set(EMAIL_REGEX.findall(html))
    faculty_emails = {e for e in all_matches if looks_like_faculty_email(e)}

    print(f"    [+] Found {len(faculty_emails)} likely faculty emails on this page.")
    return faculty_emails


if __name__ == "__main__":
    # Put all your faculty pages here
    faculty_pages = [
        "https://warnell.uga.edu/directory/faculty",
        "https://psychology.uga.edu/directory/faculty",
        "https://www.stat.uga.edu/directory/faculty",
        "https://www.math.uga.edu/directory/faculty",
        "https://foodscience.caes.uga.edu/people/faculty.html",
        "https://poultry.caes.uga.edu/people/faculty.html",
        "https://cropsoil.uga.edu/people/faculty.html",
        "https://cellbio.uga.edu/directory",
        "https://www.physast.uga.edu/directory/Regular-Faculty",
        "https://chem.uga.edu/directory/Core-Faculty",
        "https://ccrc.uga.edu/tenure-track-faculty/",
        "https://www.terry.uga.edu/faculty-and-research/expertise/management-information-systems/",
        "https://geography.uga.edu/directory/faculty",
        # add more here…
    ]

    email_to_source = {}  # email -> first page where we saw it

    for page in faculty_pages:
        try:
            emails = scrape_faculty_page(page)
            for e in emails:
                email_to_source.setdefault(e, page)
        except Exception as ex:
            print(f"    [!] Error on {page}: {ex}")

    print("\n==============================")
    print("     ALL UGA FACULTY EMAILS   ")
    print("==============================\n")

    for email in sorted(email_to_source.keys()):
        print(f"{email:35s}  ({email_to_source[email]})")

    print(f"\nTotal unique faculty emails found: {len(email_to_source)}")

    # Save to CSV
    out_file = "uga_faculty_emails.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "source_url"])
        for email in sorted(email_to_source.keys()):
            writer.writerow([email, email_to_source[email]])

    print(f"\n[+] Saved to {out_file}")
