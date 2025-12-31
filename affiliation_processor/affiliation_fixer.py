# CLEAN + DEDUPLICATED VERSION
# 100% rule-based affiliation normalization
# No ML models required - fast and deterministic

import re

# Words that should not be capitalized (except when first word or after punctuation)
DONT_CAPITALIZE = {
    "of", "and", "the", "a", "an", "in", "on", "at", "to", "for", "with", "by", "from"
}

def smart_title_final(text: str) -> str:
    """Apply smart title case to final output: lowercase articles/prepositions except after punctuation."""
    if not text:
        return text
    
    # Split by comma and period to preserve sentence/clause boundaries
    parts = []
    for part in text.replace(', ', '|,|').replace('.', '|.|').split('|'):
        if part in [',', '.', '']:
            parts.append(part)
            continue
        
        words = part.strip().split()
        result = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            # Capitalize first word of each clause/sentence, otherwise check DONT_CAPITALIZE
            if i == 0 or word_lower not in DONT_CAPITALIZE:
                result.append(word_lower.capitalize())
            else:
                result.append(word_lower)
        parts.append(' '.join(result))
    
    # Rejoin with proper spacing
    output = ''
    for i, part in enumerate(parts):
        output += part
        # Add space after comma
        if part == ',' and i + 1 < len(parts) and parts[i + 1] not in [',', '.', '']:
            output += ' '
    
    return output

COUNTRIES = {"egypt": "Egypt"}

# City to Country mapping
CITY_TO_COUNTRY = {
    "damietta": "Egypt",
    "damitta": "Egypt",  # Common misspelling
    "domitta": "Egypt",  # Common misspelling
    "dameitta": "Egypt",  # Common misspelling
    "new damietta": "Egypt",  # Normalize to just Damietta
    "new dameitta": "Egypt",  # Normalize to just Damietta
    "cairo": "Egypt",
    "tanta": "Egypt",
    "alexandria": "Egypt",
    "giza": "Egypt",
    "kafr el sheikh": "Egypt",
    "mansoura": "Egypt",
}

# City spelling corrections
CITY_CORRECTIONS = {
    "damitta": "Damietta",
    "domitta": "Damietta",
    "dameitta": "Damietta",
    "new damietta": "Damietta",  # Always normalize to Damietta (no "New")
    "new dameitta": "Damietta",  # Always normalize to Damietta (no "New")
}

# Department to Faculty mapping
DEPT_TO_FACULTY = {
    "psychology": "Faculty of Medicine",
    "comp sci": "Faculty of Engineering",
    "computer science": "Faculty of Engineering",
    "medicine": "Faculty of Medicine",
    "engineering": "Faculty of Engineering",
    "radiology": "Faculty of Medicine",
    "pediatric": "Faculty of Medicine",
    "pediatrics": "Faculty of Medicine",
    "neurosurgery": "Faculty of Medicine",
}

UNIV_ALIASES = {
    "alazhar": "Al-Azhar University",
    "al azhar": "Al-Azhar University",
    "al azher": "Al-Azhar University",  # Common misspelling
    "azhar": "Al-Azhar University",
    "azher": "Al-Azhar University",
    "cairo univ": "Cairo University",
    "cairo university": "Cairo University",
    "mansoura university": "Mansoura University",
    "mansoura univ": "Mansoura University",
}

FACULTY_WORDS = ["faculty", "college", "school"]
DEPT_WORDS = ["department", "dept"]

def clean(s):
    return re.sub(r"\s+", " ", s.strip())

def extract_department(text):
    # Skip if text starts with a title/role
    if re.match(r"(?i)^\s*(lecturer|professor|assistant professor|associate professor|resident)\s+of", text):
        # Extract the specialty after "of"
        m = re.search(r"(?i)(?:lecturer|professor|assistant professor|associate professor|resident)\s+of\s+([a-z]+)", text)
        if m:
            return m.group(1).title()
        return ""
    
    # Handle "deparmtent" misspelling
    text = re.sub(r"(?i)\bdeparmtent\b", "department", text)
    
    # Look for "department of X City Faculty" pattern - extract just X (more specific, check first)
    m = re.search(r"(?i)(?:department|dept)\s+of\s+([a-z]+)(?:\s+[a-z]+\s+faculty)", text)
    if m:
        return m.group(1).title()
    
    # Look for explicit "department of X" or "X department"
    m = re.search(r"(?i)(?:department|dept)\s+of\s+([a-z &]+)", text)
    if m:
        captured = m.group(1).title()
        return captured
    m = re.search(r"(?i)([a-z &]+)\s+(?:department|dept)", text)
    if m:
        captured = m.group(1).title()
        # Remove common misspellings from department name
        captured = captured.replace("Depridement", "").strip()
        if captured:
            return captured
    
    # Look for pattern: "Word1 Word2 faculty/facality" - extract Word1 Word2 as department
    m = re.search(r"(?i)^([a-z ]+?)\s+(?:facality|faculty|faclty)", text)
    if m:
        dept_candidate = m.group(1).strip().title()
        # Skip if it's a title/role
        if dept_candidate.lower() in ["lecturer", "professor", "assistant professor", "associate professor"]:
            return ""
        # Correct common misspellings in department names
        dept_candidate = dept_candidate.replace("Depridement", "Surgery")
        dept_candidate = dept_candidate.replace("Surgary", "Surgery")
        # Remove common non-department words
        dept_candidate = re.sub(r"\b(Of|The)\b", "", dept_candidate, flags=re.IGNORECASE).strip()
        if dept_candidate and len(dept_candidate.split()) <= 3:
            return dept_candidate
    
    # Look for pattern: "City Department_Name Center" - extract Department_Name
    m = re.search(r"(?i)^(?:[\w\s]+\s+)?([a-z]+(?:ology)?)\s+center", text)
    if m:
        dept_candidate = m.group(1).strip().title()
        if dept_candidate:
            return dept_candidate
    
    return ""

def extract_faculty(parts):
    for p in parts:
        p_lower = p.lower()
        # Check for faculty keywords (including common misspellings)
        has_faculty = (any(w in p_lower for w in FACULTY_WORDS) or 
                      "facality" in p_lower or "faclty" in p_lower)
        
        if has_faculty:
            # Try to extract "faculty of X" or "X faculty" pattern, stopping at city names or university keywords
            # Build a pattern that stops at known cities or university keywords
            m = re.search(r"(?i)((?:faculty|facality|faclty)\s+of\s+[a-z]+)(?:\s|$)", p)
            if m:
                result = m.group(1).title()
                result = result.replace("Facality", "Faculty").replace("Faclty", "Faculty")
                return result.strip()
            
            # Fallback: Extract just the faculty part, remove city names and university names
            words = p.split()
            faculty_words = []
            i = 0
            while i < len(words):
                w = words[i]
                w_lower = w.lower()
                
                # Check if this is the start of a multi-word city (including partial matches)
                is_city_start = False
                for city in CITY_TO_COUNTRY.keys():
                    if " " in city:
                        city_words = city.split()
                        # Check if the remaining words start matching this city (even with misspellings)
                        if i + len(city_words) <= len(words):
                            remaining_words = [words[j].lower() for j in range(i, i + len(city_words))]
                            remaining_str = " ".join(remaining_words)
                            if remaining_str == city:
                                is_city_start = True
                                break
                        # Also check if current word is the first word of a multi-word city
                        if w_lower == city_words[0]:
                            # Lookahead to see if next words might be the rest of the city (with misspellings)
                            if i + 1 < len(words):
                                is_city_start = True
                                break
                
                if is_city_start or w_lower in CITY_TO_COUNTRY:
                    break
                if "univ" in w_lower:
                    break
                faculty_words.append(w)
                i += 1
                
            if faculty_words:
                # Correct common misspellings
                result = " ".join(faculty_words).title()
                result = result.replace("Facality", "Faculty")
                result = result.replace("Faclty", "Faculty")
                
                # Remove trailing city words that might have slipped through
                result_words = result.split()
                cleaned = False
                while result_words and len(result_words) > 2:  # Keep at least "Faculty Of"
                    last_word_lower = result_words[-1].lower()
                    # Check if last word is a city or city prefix
                    if last_word_lower in CITY_TO_COUNTRY or last_word_lower in ['new', 'old', 'el', 'al', 'sheikh']:
                        result_words.pop()
                        cleaned = True
                    else:
                        break
                
                if result_words:
                    return " ".join(result_words)
                return result
    return ""

def extract_country(parts):
    for p in parts:
        if p.lower() in COUNTRIES:
            return COUNTRIES[p.lower()]
    return ""

def extract_university(parts):
    for p in parts:
        low = p.lower()
        # Check for exact alias match
        if low in UNIV_ALIASES:
            return UNIV_ALIASES[low]
        # Check if alias is within the part
        for alias, full_name in UNIV_ALIASES.items():
            if alias in low:
                return full_name
        # Check for "center" or "centre"
        if "center" in low or "centre" in low:
            return p.title()
        # Check for "univ" or "university" keyword
        if "univ" in low:
            # Extract just the university name, stop at city names and faculty words
            words = p.split()
            univ_words = []
            for w in words:
                w_lower = w.lower()
                if w_lower in CITY_TO_COUNTRY:
                    break
                # Stop at "Faculty" to avoid "Faculty of Medicine Mansoura University" 
                if w_lower in FACULTY_WORDS:
                    break
                univ_words.append(w)
            if univ_words:
                result = " ".join(univ_words).title()
                # Only replace "Univ" if it's not already "University"
                if "University" not in result:
                    result = result.replace("Univ", "University")
                return result
    return ""

def extract_city(parts, used):
    # Check for known cities first (including multi-word cities)
    for p in parts:
        p_lower = p.lower()
        # Check if the whole part is a city
        if p_lower in CITY_TO_COUNTRY and p not in used:
            if p_lower in CITY_CORRECTIONS:
                return CITY_CORRECTIONS[p_lower]
            return p.title()
        
        # Check for multi-word cities at the start of the part
        for city in CITY_TO_COUNTRY.keys():
            if " " in city and p_lower.startswith(city):
                if city in CITY_CORRECTIONS:
                    return CITY_CORRECTIONS[city]
                return city.title()
        
        # Check individual words and multi-word combinations
        words = p.split()
        for i in range(len(words)):
            # Try multi-word cities first
            for city in sorted(CITY_TO_COUNTRY.keys(), key=lambda x: -len(x.split())):
                if " " in city:
                    city_words = city.split()
                    if i + len(city_words) <= len(words):
                        candidate = " ".join([words[j].lower() for j in range(i, i + len(city_words))])
                        if candidate == city:
                            if city in CITY_CORRECTIONS:
                                return CITY_CORRECTIONS[city]
                            return city.title()
            
            # Single word cities
            w = words[i]
            w_lower = w.lower()
            if w_lower in CITY_TO_COUNTRY and w not in used:
                # Return corrected spelling if available
                if w_lower in CITY_CORRECTIONS:
                    return CITY_CORRECTIONS[w_lower]
                return w.title()
    
    # Fallback: return first unused part that's not a country
    for p in parts:
        p_lower = p.lower()
        # Strip "new" prefix before checking
        p_lower_stripped = re.sub(r'^new\s+', '', p_lower)
        
        if p not in used and p_lower not in COUNTRIES:
            # Return corrected spelling if available (check both original and stripped)
            if p_lower in CITY_CORRECTIONS:
                return CITY_CORRECTIONS[p_lower]
            if p_lower_stripped in CITY_CORRECTIONS:
                return CITY_CORRECTIONS[p_lower_stripped]
            if p_lower_stripped in CITY_TO_COUNTRY:
                # Strip "New" prefix from the title case version too
                result = re.sub(r'^New\s+', '', p.title(), flags=re.IGNORECASE)
                return result
            return p.title()
    return ""

def normalize_affiliation(raw):
    raw = clean(raw)
    # Remove parentheses but keep the content
    raw = re.sub(r"[()]", " ", raw)
    raw = clean(raw)
    parts = [clean(p) for p in re.split(r"[,\n]", raw) if p.strip()]

    dept = extract_department(raw)
    faculty = extract_faculty(parts)
    country = extract_country(parts)
    
    # Extract university - also check within each part if "university" appears
    university = extract_university(parts)
    
    # If university not found in parts, try to extract from space-separated tokens
    if not university:
        for part in parts:
            tokens = part.split()
            for token in tokens:
                if "univ" in token.lower() or token.lower() in UNIV_ALIASES:
                    # Found university keyword, try to extract it
                    temp_parts = []
                    for t in tokens:
                        temp_parts.append(t)
                        if "univ" in t.lower():
                            break
                    university = extract_university([" ".join(temp_parts)])
                    if university:
                        break
            if university:
                break
    
    # If still no department found, check if first part could be a department
    # (common pattern: "Department Name, Faculty, University, City")
    if not dept and parts:
        first = parts[0].lower()
        # If first part doesn't contain faculty/university keywords, it's likely a department
        cities_list = list(CITY_TO_COUNTRY.keys())
        has_faculty_word = (any(w in first for w in FACULTY_WORDS) or 
                           "facality" in first or "faclty" in first)
        
        # Skip if it looks like a center (will be handled as university)
        if "center" not in first and "centre" not in first:
            if not any(w in first for w in ["univ"] + cities_list) and not has_faculty_word:
                if first not in UNIV_ALIASES:
                    # Extract department name, clean up common misspellings
                    dept_name = parts[0].title()
                    # Remove trailing words that look like misspellings
                    dept_name = re.sub(r"\s+(Facality|Faclty|Of|Medicine|Domitta|Damitta)\b.*$", "", dept_name, flags=re.IGNORECASE)
                    if dept_name.strip():
                        dept = dept_name.strip()

    # Track all used text (case-insensitive) to avoid duplicates
    used_lower = set()
    
    # Add extracted entities to used set (normalized)
    if dept:
        used_lower.add(dept.lower())
    if faculty:
        used_lower.add(faculty.lower())
    if country:
        used_lower.add(country.lower())
    if university:
        used_lower.add(university.lower())

    # University extraction relies on rule-based methods only
    # No NER fallback needed - the rule-based extraction is comprehensive

    # Build used set for city extraction (case-insensitive comparison)
    used_parts = set()
    for part in parts:
        part_lower = part.lower()
        if part_lower in used_lower:
            used_parts.add(part)
            continue
        # Check substring matches
        for used_item in used_lower:
            if part_lower in used_item or used_item in part_lower:
                used_parts.add(part)
                break

    city = extract_city(parts, used_parts)
    
    # If city not found but university contains a city name, extract it
    if not city and university:
        for city_name in CITY_TO_COUNTRY.keys():
            if city_name in university.lower():
                if city_name in CITY_CORRECTIONS:
                    city = CITY_CORRECTIONS[city_name]
                else:
                    city = city_name.title()
                break
    
    # Infer faculty from department if not found
    if dept and not faculty:
        dept_lower = dept.lower()
        for key, fac in DEPT_TO_FACULTY.items():
            if key in dept_lower:
                faculty = fac
                break
    
    # Infer country from city if not found
    if city and not country:
        city_lower = city.lower()
        if city_lower in CITY_TO_COUNTRY:
            country = CITY_TO_COUNTRY[city_lower]

    out = []
    if dept:
        out.append(f"Department of {dept}")
    if faculty:
        out.append(faculty)
    if university:
        out.append(university)
    if city:
        out.append(city)
    if country:
        out.append(country)

    result = ", ".join(out) + "."
    
    # Apply smart title case to final output
    return smart_title_final(result)

# ----------------------------------------------------------------------------------------------------
# TESTS (uncomment to run)
# tests = [
#     "Psychology department, Damietta, alazhar",
#     "Dept of Comp Sci, Faculty of Engineering, Cairo Univ, Egypt",
#     "School of Medicine, Tanta, Egypt",
#     "Orthopedic surgery , faculty of medicine,al-azhar university damitta",
#     "Orthopedic Surgery Department, Damietta Faculty of Medicine, Al-Azhar University, Egypt.",
#     "Orthopedic depridement facality of medicine domitta Al azher",
#     "Kafr El Sheikh Ophthalmology Center",
#     "Faculty of Medicine, Al-Azhar university, Cairo",
#     "Department of Orthopedic Surgery, Damietta Faculty of Medicine, Al-Azhar University, Damietta, Egypt.",
#     "Department of Otorhinolaryngology, Damietta Faculty of Medicine, Al-Azhar University, Damietta, Egypt.",
#     "Department of Audiovestibular Medicine,Faculty of Medicine Mansoura University, Mansoura, Egypt",
#     "Deparmtent of Clinical Pathology, Damietta Faculty of Medicine, Al-Azhar University, Damietta, Egypt",
#     "lecturer of otorhinolaryngolgy,al azhar faculty of medicine new dameitta",
#     "Department of Pediatrics,Faculty of Medicine, Al-Azhar University, Damitta, Egypt",
#     "Pediatric Department, Al-Azhar Faculty of Medicine (Damietta)",
#     "Pediatric Department, Al-Azhar faculty of Medicine (Damietta)",
#     "Department of Radiology",
#     "Resident of Neurosurgery, Al-Azhar University Hospitals, Damietta, Egypt",
#     "Neurosurgery Department, Damietta Faculty of Medicine, Al-Azhar University, Egypt",
#     "Department of Neurosurgery Damietta Faculty of Medicine, Al-Azhar University"
# ]
#
# for t in tests:
#     print("IN: ", t)
#     print("OUT:", normalize_affiliation(t))
#     print()

# ----------------------------------------------------------------------------------------------------
