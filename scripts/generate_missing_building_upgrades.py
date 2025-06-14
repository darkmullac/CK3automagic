import os
import re

SOURCE_DIR = 'paradox_building_sourcefiles_DO_NOT_MODIFY'
TARGET_FILE = 'common/scripted_effects/build_scripted_effect.txt'
EXCLUDE_FILES = {'99_background_graphics_buildings.txt', '_buildings.info'}

def parse_building_chains():
    chains = {}
    for fname in sorted(os.listdir(SOURCE_DIR)):
        if not fname.endswith('.txt') or fname in EXCLUDE_FILES:
            continue
        path = os.path.join(SOURCE_DIR, fname)
        with open(path, encoding='utf-8') as f:
            text = f.read()
        for m in re.finditer(r'^\s*([A-Za-z0-9_]+)_([0-9]+)\s*=\s*{', text, re.M):
            base = m.group(1)
            tier = int(m.group(2))
            chains.setdefault(base, set()).add(tier)
    return chains

def parse_existing_effects():
    """Return mapping of building chains to tiers already handled."""
    with open(TARGET_FILE, encoding="utf-8") as f:
        text = f.read()

    tiers_by_base = {}
    pattern = r"([A-Za-z0-9_]+)_([0-9]+)"
    for base, tier in re.findall(pattern, text):
        try:
            tier_num = int(tier)
        except ValueError:
            continue
        tiers_by_base.setdefault(base, set()).add(tier_num)
    return tiers_by_base

def generate_logic(base, tiers, existing_tiers):
    """Generate upgrade blocks for tiers not already present."""
    tiers_to_add = sorted(set(tiers) - set(existing_tiers))
    if len(tiers) <= 1 or not tiers_to_add:
        return ""

    lines = []
    for t in tiers_to_add:
        building = f"{base}_{t:02d}"
        lines.append("if = {")
        lines.append("    limit = {")
        lines.append(f"        NOT = {{ has_building_or_higher = {building} }}")
        lines.append(f"        can_construct_building = {building}")
        lines.append("    }")
        lines.append(f"    add_building = {building}")
        lines.append("}")
    return "\n".join(lines)

def main():
    chains = parse_building_chains()
    existing = parse_existing_effects()
    for base, tiers in sorted(chains.items()):
        existing_tiers = existing.get(base, set())
        logic = generate_logic(base, tiers, existing_tiers)
        if logic:
            name = base.replace('_', ' ').capitalize()
            print(f"\n#{name}\n{logic}\n")

if __name__ == '__main__':
    main()
