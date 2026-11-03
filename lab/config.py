from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_inventory(path=ROOT / "inventory.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def devices_of_type(inventory, kind):
    return [d for d in inventory["devices"] if d["type"] == kind]
    