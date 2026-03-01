import unittest

from SmartAidKit import (
    FirstAidKit,
    KitItem,
    Medicine,
    add_medicine,
    can_take,
    next_dose_time_minutes,
    remaining_today,
    remove_medicine,
    total_units,
)


class TestSmartFirstAidKit(unittest.TestCase):
    # add_medicine
    def test_add_medicine_new_item(self):
        ibuprofen = Medicine(name="Ibuprofen", dose_mg=200, max_per_day=6, min_age=12)
        kit = FirstAidKit(items=[])
        kit2 = add_medicine(kit, ibuprofen, qty=1)

        expected = 1
        actual = len(kit2.items)
        self.assertTrue(
            actual == expected,
            f"Добавление нового лекарства в пустую аптечку.\n"
            f"Дано: лекарство='{ibuprofen.name}', qty=1.\n"
            f"Ожидалось: число позиций={expected}. Получено: число позиций={actual}.",
        )

    def test_add_medicine_merges_qty(self):
        ibuprofen = Medicine(name="Ibuprofen", dose_mg=200, max_per_day=6, min_age=12)
        kit = FirstAidKit(items=[KitItem(medicine=ibuprofen, qty=1)])
        kit2 = add_medicine(kit, ibuprofen, qty=2)

        expected = 3
        actual = kit2.items[0].qty
        self.assertTrue(
            actual == expected,
            f"Добавление лекарства, которое уже есть в аптечке (должно суммироваться).\n"
            f"Дано: '{ibuprofen.name}' было qty=1, добавили qty=2.\n"
            f"Ожидалось: qty={expected}. Получено: qty={actual}.",
        )

    # remove_medicine
    def test_remove_medicine_partial(self):
        paracetamol = Medicine(name="Paracetamol", dose_mg=500, max_per_day=4, min_age=6)
        kit = FirstAidKit(items=[KitItem(medicine=paracetamol, qty=3)])
        kit2 = remove_medicine(kit, "Paracetamol", qty=2)

        expected = 1
        actual = kit2.items[0].qty
        self.assertTrue(
            actual == expected,
            f"Частичное удаление количества лекарства.\n"
            f"Дано: 'Paracetamol' было qty=3, удалили qty=2.\n"
            f"Ожидалось: осталось qty={expected}. Получено: осталось qty={actual}.",
        )

    def test_remove_medicine_remove_all(self):
        paracetamol = Medicine(name="Paracetamol", dose_mg=500, max_per_day=4, min_age=6)
        kit = FirstAidKit(items=[KitItem(medicine=paracetamol, qty=2)])
        kit2 = remove_medicine(kit, "Paracetamol", qty=2)

        expected = 0
        actual = len(kit2.items)
        self.assertTrue(
            actual == expected,
            f"Полное удаление позиции лекарства из аптечки.\n"
            f"Дано: 'Paracetamol' было qty=2, удалили qty=2.\n"
            f"Ожидалось: число позиций={expected}. Получено: число позиций={actual}.",
        )

    def test_remove_medicine_not_found(self):
        med = Medicine(name="Ibuprofen", dose_mg=50, max_per_day=2, min_age=0)
        kit = FirstAidKit(items=[KitItem(medicine=med, qty=1)])

        with self.assertRaises(
            ValueError,
            msg="Удаление отсутствующего лекарства.\n"
                "Дано: в аптечке есть только 'Ibuprofen'. Пытаемся удалить 'Paracetamol'.\n"
                "Ожидалось: ValueError. Получено: ошибки не было.",
        ):
            remove_medicine(kit, "Paracetamol", qty=1)

    # total_units
    def test_total_units(self):
        a = Medicine(name="A", dose_mg=100, max_per_day=2, min_age=0)
        b = Medicine(name="B", dose_mg=50, max_per_day=3, min_age=0)
        kit = FirstAidKit(items=[KitItem(medicine=a, qty=2), KitItem(medicine=b, qty=3)])

        expected = 5
        actual = total_units(kit)
        self.assertTrue(
            actual == expected,
            f"Подсчёт общего количества единиц (qty) во всей аптечке.\n"
            f"Дано: A=2, B=3.\n"
            f"Ожидалось: всего qty={expected}. Получено: всего qty={actual}.",
        )

    # can_take
    def test_can_take_requires_prescription(self):
        med = Medicine(name="Antibiotic", dose_mg=500, max_per_day=3, min_age=18, requires_prescription=True)
        actual = can_take(med, age=25, taken_today=0, has_prescription=False)

        self.assertFalse(
            actual,
            f"Проверка запрета на лекарство при отсутствии рецепта.\n"
            f"Дано: '{med.name}', requires_prescription=True, has_prescription=False.\n"
            f"Ожидалось: False. Получено: {actual}.",
        )

    def test_can_take_age_limit(self):
        med = Medicine(name="Strong", dose_mg=400, max_per_day=2, min_age=16)

        actual = can_take(med, age=12, taken_today=0, has_prescription=True)
        self.assertFalse(
            actual,
            f"Проверка запрета на лекарство при недостигнутом возрасте.\n"
            f"Дано: '{med.name}', min_age=16, age=12.\n"
            f"Ожидалось: False. Получено: {actual}.",
        )

    def test_can_take_within_limit(self):
        med = Medicine(name="Light", dose_mg=200, max_per_day=4, min_age=6)

        actual = can_take(med, age=10, taken_today=2, has_prescription=False)
        self.assertTrue(
            actual,
            f"Проверка суточного лимита.\n"
            f"Дано: '{med.name}', max_per_day=4, taken_today=2.\n"
            f"Ожидалось: True. Получено: {actual}.",
        )

    # remaining_today
    def test_remaining_today(self):
        med = Medicine(name="C", dose_mg=100, max_per_day=4, min_age=0)

        expected = 1
        actual = remaining_today(med, taken_today=3)
        self.assertTrue(
            actual == expected,
            f"Вывод доз, которых осталось на сегодня.\n"
            f"Дано: '{med.name}', max_per_day=4, уже принято=3.\n"
            f"Ожидалось: осталось={expected}. Получено: осталось={actual}.",
        )

    def test_remaining_today_zero(self):
        med = Medicine(name="D", dose_mg=100, max_per_day=4, min_age=0)

        expected = 0
        actual = remaining_today(med, taken_today=10)
        self.assertTrue(
            actual == expected,
            f"Остаток доз не должен быть отрицательным.\n"
            f"Дано: '{med.name}', max_per_day=4, уже принято=10.\n"
            f"Ожидалось: осталось={expected}. Получено: осталось={actual}.",
        )

    # next_dose_time_minutes
    def test_next_dose_time_minutes(self):
        expected = 360
        actual = next_dose_time_minutes(90, 6)
        self.assertTrue(
            actual == expected,
            f"Расчёт через сколько минут можно принять следующую дозу.\n"
            f"Дано: прошло=90 мин, интервал=6 часов (=360 мин).\n"
            f"Ожидалось: через {expected} мин. Получено: через {actual} мин.",
        )


if __name__ == "__main__":
    unittest.main()
