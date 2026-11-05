from reactivation_cleanup import to_row, to_sql, check_suppress
P = {"id": "01X", "attributes": {"email": "a@b.fr", "phone_number": None, "first_name": "Jo'e", "last_name": None, "location": {"country": "FR", "zip": "75001"}, "created": "2024-01-01T00:00:00+00:00"}}
def test_row(): assert to_row(P)["email"] == "a@b.fr" and to_row(P)["country"] == "FR"
def test_sql_escapes_and_targets_archive():
    s = to_sql([to_row(P)]); assert "Jo''e" in s and s.startswith("insert into klaviyo_audience_archive") and "'X8Wwag'" in s
def test_sql_empty(): assert to_sql([]) == ""
def test_guard_refuses_unarchived(): assert check_suppress([1, 2], 1, True).startswith("REFUS")
def test_guard_simulation_without_confirm(): assert check_suppress([1, 2], 2, False) == "SIMULATION"
def test_guard_ok(): assert check_suppress([1, 2], 2, True) == "OK"
