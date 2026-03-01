from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Medicine:
    name: str
    dose_mg: int
    max_per_day: int
    min_age: int
    requires_prescription: bool = False


@dataclass(frozen=True)
class KitItem:
    medicine: Medicine
    qty: int


@dataclass(frozen=True)
class FirstAidKit:
    items: List[KitItem]


def validate_catalog(catalog: Dict[str, Medicine]) -> None:
    if not catalog:
        raise ValueError("Список лекарств пуст. Добавьте хотя бы одно лекарство.")
    for name, med in catalog.items():
        if name != med.name:
            raise ValueError("Ошибка в списке лекарств: названия не совпадают. Проверьте названия лекарств.")
        if med.dose_mg <= 0:
            raise ValueError(f"Для лекарства «{med.name}» указана неверная дозировка. Дозировка должна быть больше нуля.")
        if med.max_per_day <= 0:
            raise ValueError(f"Для лекарства «{med.name}» указана неверная суточная норма. Она должна быть больше нуля.")
        if med.min_age < 0:
            raise ValueError(f"Для лекарства «{med.name}» указан неверный минимальный возраст.")


def parse_intake_line(line: str) -> Tuple[str, int]:
    cleaned = line.strip()
    if not cleaned:
        raise ValueError("Пустая строка. Введите название лекарства (например: «Ибупрофен») или «Ибупрофен x2».")

    parts = cleaned.split("x")
    if len(parts) == 1:
        return cleaned, 1

    if len(parts) != 2:
        raise ValueError("Неверный формат. Пример: «Ибупрофен x2» (где 2 — количество).")

    name = parts[0].strip()
    qty_str = parts[1].strip()
    if not name or not qty_str.isdigit():
        raise ValueError("Неверный формат. Пример: «Ибупрофен x2» (где 2 — количество).")

    qty = int(qty_str)
    if qty <= 0:
        raise ValueError("Количество должно быть больше нуля.")
    return name, qty


def add_medicine(kit: FirstAidKit, medicine: Medicine, qty: int = 1) -> FirstAidKit:
    if qty <= 0:
        raise ValueError("Количество должно быть больше нуля.")

    new_items: List[KitItem] = []
    added = False

    for it in kit.items:
        if it.medicine.name == medicine.name:
            new_items.append(KitItem(medicine=medicine, qty=it.qty + qty))
            added = True
        else:
            new_items.append(it)

    if not added:
        new_items.append(KitItem(medicine=medicine, qty=qty))

    return FirstAidKit(items=new_items)


def remove_medicine(kit: FirstAidKit, name: str, qty: Optional[int] = None) -> FirstAidKit:
    if qty is not None and qty <= 0:
        raise ValueError("Количество должно быть больше нуля.")

    new_items: List[KitItem] = []
    removed_any = False

    for it in kit.items:
        if it.medicine.name != name:
            new_items.append(it)
            continue
        removed_any = True
        if qty is None or qty >= it.qty:
            continue
        new_items.append(KitItem(medicine=it.medicine, qty=it.qty - qty))

    if not removed_any:
        raise ValueError("Лекарство не найдено в аптечке.")

    return FirstAidKit(items=new_items)


def total_units(kit: FirstAidKit) -> int:
    return sum(it.qty for it in kit.items)


def can_take(
    medicine: Medicine,
    age: int,
    taken_today: int,
    has_prescription: bool = False,
) -> bool:
    if age < medicine.min_age:
        return False
    if medicine.requires_prescription and not has_prescription:
        return False
    return taken_today < medicine.max_per_day


def remaining_today(medicine: Medicine, taken_today: int) -> int:
    left = medicine.max_per_day - taken_today
    return left if left > 0 else 0


def next_dose_time_minutes(last_taken_minutes: int, interval_hours: int) -> int:
    if interval_hours <= 0:
        raise ValueError("Интервал должен быть больше нуля часов.")
    return last_taken_minutes + interval_hours * 60


def format_kit_report(kit: FirstAidKit) -> List[str]:
    lines: List[str] = []
    lines.append("=== Умная аптечка ===")
    for it in kit.items:
        line = f"{it.medicine.name} x{it.qty} ({it.medicine.dose_mg} мг)"
        lines.append(line)
    lines.append(f"Всего единиц: {total_units(kit)}")
    return lines


if __name__ == "__main__":
    catalog = {
        "Ибупрофен": Medicine(name="Ибупрофен", dose_mg=200, max_per_day=6, min_age=12),
        "Антибиотик": Medicine(
            name="Антибиотик",
            dose_mg=500,
            max_per_day=3,
            min_age=18,
            requires_prescription=True,
        ),
    }
    validate_catalog(catalog)
    kit = FirstAidKit(items=[])
    kit = add_medicine(kit, catalog["Ибупрофен"], qty=4)
    kit = add_medicine(kit, catalog["Антибиотик"], qty=2)
    for line in format_kit_report(kit):
        print(line)
