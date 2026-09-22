from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import ROOT, load_module


OLD_RECURRENCE_COLS = """
    (SELECT rr.ZFREQUENCY FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_frequency,
    (SELECT rr.ZINTERVAL FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_interval,
    (SELECT rr.ZOCCURRENCECOUNT FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_count,
    (SELECT rr.ZENDDATE FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_end_date,
    (SELECT rr.ZDAYSOFTHEWEEK FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_days_of_week,
    (SELECT rr.ZDAYSOFTHEMONTH FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_days_of_month,
    (SELECT rr.ZMONTHSOFTHEYEAR FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_months_of_year,
    (SELECT rr.ZDAYSOFTHEYEAR FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_days_of_year,
    (SELECT rr.ZWEEKSOFTHEYEAR FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_weeks_of_year,
    (SELECT rr.ZSETPOSITIONS FROM ZREMCDOBJECT rr WHERE rr.ZREMINDER4 = r.Z_PK AND rr.ZMARKEDFORDELETION = 0 AND rr.Z_ENT = 34 ORDER BY rr.Z_PK LIMIT 1) AS recurrence_set_positions"""


def _reminder_select_prefix():
    return (
        "r.Z_PK, r.ZTITLE, r.ZNOTES, r.ZCOMPLETED, r.ZFLAGGED, r.ZPRIORITY, "
        "r.ZISURGENTSTATEENABLEDFORCURRENTUSER AS ZISURGENTSTATEENABLEDFORCURRENTUSER, "
        "r.ZDUEDATEDELTAALERTSDATA AS ZDUEDATEDELTAALERTSDATA, "
        "r.ZDUEDATE AS ZDUEDATE, r.ZDISPLAYDATEDATE AS ZDISPLAYDATEDATE, "
        "r.ZALLDAY, r.ZCOMPLETIONDATE, r.ZCREATIONDATE, "
        "r.ZPARENTREMINDER, r.ZLIST, r.ZICSURL, r.ZCKIDENTIFIER, l.ZNAME as list_name, "
    )


class EntrypointTests(unittest.TestCase):
    def test_wrapper_imports_and_runs_cli_version(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "remctl"), "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1.7.0", result.stdout)

    def test_wrapper_module_exposes_main(self):
        module = load_module("remctl_wrapper_test", "remctl")
        self.assertTrue(callable(module.main))


class StorePathCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.remctl = load_module("remctl_store_cache_test", "remctl_main.py")

    def _store_db(self, path, reminders=1, active=1, objects=1):
        db = sqlite3.connect(path)
        db.executescript("""
            CREATE TABLE ZREMCDREMINDER (
                Z_PK INTEGER PRIMARY KEY,
                ZCOMPLETED INTEGER DEFAULT 0,
                ZMARKEDFORDELETION INTEGER DEFAULT 0
            );
            CREATE TABLE ZREMCDBASELIST (
                Z_PK INTEGER PRIMARY KEY,
                ZNAME TEXT,
                ZMARKEDFORDELETION INTEGER DEFAULT 0
            );
            CREATE TABLE ZREMCDOBJECT (
                Z_PK INTEGER PRIMARY KEY,
                ZMARKEDFORDELETION INTEGER DEFAULT 0,
                ZMODIFIEDDATE REAL
            );
        """)
        db.execute("INSERT INTO ZREMCDBASELIST (Z_PK, ZNAME) VALUES (1, 'Inbox')")
        for i in range(reminders):
            completed = 0 if i < active else 1
            db.execute(
                "INSERT INTO ZREMCDREMINDER (Z_PK, ZCOMPLETED) VALUES (?, ?)",
                (i + 1, completed),
            )
        for i in range(objects):
            db.execute(
                "INSERT INTO ZREMCDOBJECT (Z_PK, ZMODIFIEDDATE) VALUES (?, ?)",
                (i + 1, 100 + i),
            )
        db.commit()
        db.close()

    def test_find_main_db_path_cache_hit_skips_scoring(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            store = tmp / "stores"
            config = tmp / "config"
            store.mkdir()
            active = store / "Data-active.sqlite"
            other = store / "Data-other.sqlite"
            self._store_db(active, reminders=2, active=2, objects=2)
            self._store_db(other, reminders=0, active=0, objects=0)
            with (
                mock.patch.object(self.remctl, "STORE_DIR", store),
                mock.patch.object(self.remctl, "CONFIG_DIR", config),
                mock.patch.object(self.remctl, "reminders_store_access_error", return_value=None),
            ):
                first = self.remctl.find_main_db_path()
                self.assertEqual(first, active)
                cache = config / "store-path-cache.json"
                self.assertTrue(cache.is_file())
                self.assertEqual(json.loads(cache.read_text())["chosen"], str(active))
                with mock.patch.object(self.remctl, "reminders_db_score") as score:
                    second = self.remctl.find_main_db_path()
                self.assertEqual(second, active)
                score.assert_not_called()

    def test_find_main_db_path_cache_misses_when_mtime_changes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            store = tmp / "stores"
            config = tmp / "config"
            store.mkdir()
            first_db = store / "Data-a.sqlite"
            second_db = store / "Data-b.sqlite"
            self._store_db(first_db, reminders=3, active=3, objects=3)
            self._store_db(second_db, reminders=0, active=0, objects=0)
            with (
                mock.patch.object(self.remctl, "STORE_DIR", store),
                mock.patch.object(self.remctl, "CONFIG_DIR", config),
                mock.patch.object(self.remctl, "reminders_store_access_error", return_value=None),
            ):
                self.assertEqual(self.remctl.find_main_db_path(), first_db)
                Path(f"{first_db}-wal").write_bytes(b"x" * 4096)
                with mock.patch.object(
                    self.remctl, "reminders_db_score", wraps=self.remctl.reminders_db_score
                ) as score:
                    self.assertEqual(self.remctl.find_main_db_path(), first_db)
                self.assertGreaterEqual(score.call_count, 1)

    def test_find_main_db_path_invalidates_when_candidates_differ(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            store = tmp / "stores"
            config = tmp / "config"
            store.mkdir()
            only = store / "Data-only.sqlite"
            extra = store / "Data-extra.sqlite"
            self._store_db(only, reminders=1, active=1, objects=1)
            with (
                mock.patch.object(self.remctl, "STORE_DIR", store),
                mock.patch.object(self.remctl, "CONFIG_DIR", config),
                mock.patch.object(self.remctl, "reminders_store_access_error", return_value=None),
            ):
                self.assertEqual(self.remctl.find_main_db_path(), only)
                self._store_db(extra, reminders=8, active=8, objects=8)
                with mock.patch.object(
                    self.remctl, "reminders_db_score", wraps=self.remctl.reminders_db_score
                ) as score:
                    chosen = self.remctl.find_main_db_path()
                self.assertEqual(chosen, extra)
                self.assertGreaterEqual(score.call_count, 2)


class RemColsRecurrenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.remctl = load_module("remctl_rem_cols_test", "remctl_main.py")

    def _db(self):
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        db.executescript("""
            CREATE TABLE ZREMCDREMINDER (
                Z_PK INTEGER PRIMARY KEY, ZTITLE TEXT, ZNOTES TEXT, ZCOMPLETED INTEGER,
                ZFLAGGED INTEGER, ZPRIORITY INTEGER, ZISURGENTSTATEENABLEDFORCURRENTUSER INTEGER,
                ZDUEDATEDELTAALERTSDATA TEXT, ZDUEDATE REAL, ZDISPLAYDATEDATE REAL, ZALLDAY INTEGER,
                ZCOMPLETIONDATE REAL, ZCREATIONDATE REAL, ZPARENTREMINDER INTEGER, ZLIST INTEGER,
                ZICSURL TEXT, ZCKIDENTIFIER TEXT, ZACCOUNT INTEGER, ZMARKEDFORDELETION INTEGER
            );
            CREATE TABLE ZREMCDBASELIST (Z_PK INTEGER PRIMARY KEY, ZNAME TEXT);
            CREATE TABLE ZREMCDOBJECT (
                Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, ZREMINDER4 INTEGER,
                ZMARKEDFORDELETION INTEGER, ZFREQUENCY INTEGER, ZINTERVAL INTEGER,
                ZOCCURRENCECOUNT INTEGER, ZENDDATE REAL, ZDAYSOFTHEWEEK TEXT,
                ZDAYSOFTHEMONTH TEXT, ZMONTHSOFTHEYEAR TEXT, ZDAYSOFTHEYEAR TEXT,
                ZWEEKSOFTHEYEAR TEXT, ZSETPOSITIONS TEXT
            );
        """)
        db.execute("INSERT INTO ZREMCDBASELIST (Z_PK, ZNAME) VALUES (1, 'Inbox')")
        db.execute(
            "INSERT INTO ZREMCDREMINDER VALUES "
            "(1, 'Weekly', NULL, 0, 0, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, "
            "1, NULL, 'CK-1', 1, 0)"
        )
        db.execute(
            "INSERT INTO ZREMCDREMINDER VALUES "
            "(2, 'Once', NULL, 0, 0, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, "
            "1, NULL, 'CK-2', 1, 0)"
        )
        db.execute(
            "INSERT INTO ZREMCDOBJECT VALUES "
            "(10, 34, 1, 0, 1, 1, 0, NULL, '[{\"dayOfTheWeek\": 2}]', NULL, NULL, NULL, NULL, NULL)"
        )
        db.execute(
            "INSERT INTO ZREMCDOBJECT VALUES "
            "(11, 34, 1, 0, 2, 3, 5, 123.0, NULL, '[15]', NULL, NULL, NULL, NULL)"
        )
        db.execute(
            "INSERT INTO ZREMCDOBJECT VALUES "
            "(12, 34, 1, 1, 0, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL)"
        )
        db.execute(
            "INSERT INTO ZREMCDOBJECT VALUES "
            "(13, 99, 2, 0, 0, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL)"
        )
        return db

    def test_rem_cols_join_matches_historical_subqueries(self):
        db = self._db()
        try:
            cols = self.remctl.rem_cols(db)
            self.assertNotIn("SELECT rr.ZFREQUENCY", cols)
            self.assertIn("rr.ZFREQUENCY AS recurrence_frequency", cols)
            join_sql = self.remctl.rem_from()
            self.assertIn("LEFT JOIN", join_sql)
            new_rows = db.execute(
                f"SELECT {cols} FROM {join_sql} "
                "WHERE r.ZMARKEDFORDELETION = 0 ORDER BY r.Z_PK"
            ).fetchall()
            old_sql = (
                f"SELECT {_reminder_select_prefix()}{OLD_RECURRENCE_COLS} "
                "FROM ZREMCDREMINDER r LEFT JOIN ZREMCDBASELIST l ON r.ZLIST = l.Z_PK "
                "WHERE r.ZMARKEDFORDELETION = 0 ORDER BY r.Z_PK"
            )
            old_rows = db.execute(old_sql).fetchall()
            self.assertEqual(len(new_rows), 2)
            keys = new_rows[0].keys()
            for new_row, old_row in zip(new_rows, old_rows):
                self.assertEqual([new_row[k] for k in keys], [old_row[k] for k in keys])
            self.assertEqual(new_rows[0]["recurrence_frequency"], 1)
            self.assertEqual(new_rows[0]["recurrence_interval"], 1)
            self.assertIsNone(new_rows[1]["recurrence_frequency"])
            payload = self.remctl.recurrence_from_row(new_rows[0])
            self.assertEqual(payload["frequency"], "weekly")
            self.assertEqual(payload["daysOfWeek"], [2])
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
