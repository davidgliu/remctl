from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from helpers import load_module


class ResetDailyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.remctl = load_module("remctl_reset_daily_test", "remctl_main.py")

    def _row(self, **overrides):
        row = {
            "Z_PK": 1,
            "ZTITLE": "Stretch",
            "ZALLDAY": 0,
            "ZDUEDATE": None,
            "ZDISPLAYDATEDATE": None,
            "recurrence_frequency": 0,
            "recurrence_interval": 1,
            "recurrence_count": None,
            "recurrence_end_date": None,
            "recurrence_days_of_week": None,
            "recurrence_days_of_month": None,
            "recurrence_months_of_year": None,
            "recurrence_days_of_year": None,
            "recurrence_weeks_of_year": None,
            "recurrence_set_positions": None,
        }
        row.update(overrides)
        return row

    def _due_db(self):
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
        return db

    def _insert(self, db, pk, title, *, due, all_day=0, completed=0, deleted=0,
                frequency=None, interval=1):
        db.execute(
            "INSERT INTO ZREMCDREMINDER VALUES "
            "(?, ?, NULL, ?, 0, 0, 0, NULL, ?, ?, ?, NULL, NULL, NULL, "
            "1, NULL, ?, 1, ?)",
            (pk, title, completed, due, due, all_day, f"CK-{pk}", deleted),
        )
        if frequency is not None:
            db.execute(
                "INSERT INTO ZREMCDOBJECT VALUES "
                "(?, 34, ?, 0, ?, ?, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL)",
                (pk + 100, pk, frequency, interval),
            )

    def test_is_daily_repeat_matches_frequency_zero_interval_one(self):
        self.assertTrue(self.remctl.is_daily_repeat(self._row()))
        self.assertTrue(self.remctl.is_daily_repeat(self._row(recurrence_interval=None)))
        self.assertFalse(self.remctl.is_daily_repeat(self._row(recurrence_frequency=1)))
        self.assertFalse(self.remctl.is_daily_repeat(self._row(recurrence_interval=2)))
        self.assertFalse(self.remctl.is_daily_repeat(self._row(recurrence_frequency=None)))

    def test_due_spec_preserves_time_and_all_day(self):
        now = datetime(2026, 9, 22, 16, 45)
        timed = self._row(ZDUEDATE=self.remctl.to_ts(datetime(2026, 9, 20, 9, 30)))
        all_day = self._row(ZALLDAY=1, ZDISPLAYDATEDATE=self.remctl.to_ts(datetime(2026, 9, 20)))
        self.assertEqual(self.remctl.due_spec_for_local_today(timed, now=now), "2026-09-22 09:30")
        self.assertEqual(self.remctl.due_spec_for_local_today(all_day, now=now), "2026-09-22")
        self.assertTrue(self.remctl.due_spec_is_all_day("2026-09-22"))
        self.assertFalse(self.remctl.due_spec_is_all_day("2026-09-22 09:30"))

    def test_q_overdue_daily_selects_only_overdue_daily(self):
        db = self._due_db()
        self.remctl._REMINDER_COLUMN_CACHE.clear()
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = self.remctl.to_ts(today - timedelta(days=1))
            tomorrow = self.remctl.to_ts(today + timedelta(days=1))
            later_today = self.remctl.to_ts(today.replace(hour=18))
            self._insert(db, 1, "Daily overdue", due=yesterday, frequency=0, interval=1)
            self._insert(db, 2, "Weekly overdue", due=yesterday, frequency=1, interval=1)
            self._insert(db, 3, "Daily tomorrow", due=tomorrow, frequency=0, interval=1)
            self._insert(db, 4, "Daily later today", due=later_today, frequency=0, interval=1)
            self._insert(db, 5, "Daily x2 overdue", due=yesterday, frequency=0, interval=2)
            self._insert(db, 6, "No repeat overdue", due=yesterday)
            self._insert(
                db, 7, "Completed daily overdue", due=yesterday,
                completed=1, frequency=0, interval=1,
            )
            self._insert(
                db, 8, "Deleted daily overdue", due=yesterday,
                deleted=1, frequency=0, interval=1,
            )
            names = [row["ZTITLE"] for row in self.remctl.q_overdue_daily(db)]
            self.assertEqual(names, ["Daily overdue"])
        finally:
            db.close()
            self.remctl._REMINDER_COLUMN_CACHE.clear()

    def test_cmd_reset_daily_edits_only_matches(self):
        now = datetime(2026, 9, 22, 8, 0)
        yesterday = self.remctl.to_ts(datetime(2026, 9, 21, 7, 15))
        match = self._row(
            Z_PK=11, ZTITLE="Daily overdue", ZDUEDATE=yesterday, ZALLDAY=0,
        )
        edited = []

        def fake_edit(args):
            edited.append((args.id, args.due, args.json))
            print(json.dumps({"status": "updated", "id": args.id, "title": "Daily overdue"}))

        FakeDateTime = type("FakeDateTime", (datetime,), {"now": staticmethod(lambda tz=None: now)})
        with (
            mock.patch.object(self.remctl, "open_db", return_value=object()),
            mock.patch.object(self.remctl, "q_overdue_daily", return_value=[match]),
            mock.patch.object(self.remctl, "datetime", FakeDateTime),
            mock.patch.object(self.remctl, "cmd_edit", side_effect=fake_edit),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            self.remctl.cmd_reset_daily(SimpleNamespace(json=True))

        self.assertEqual(edited, [(11, "2026-09-22 07:15", True)])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["matched"], 1)
        self.assertEqual(payload["updated"], 1)
        self.assertEqual(payload["reminders"][0]["id"], 11)
        self.assertEqual(payload["reminders"][0]["due"], "2026-09-22 07:15")

    def test_cmd_reset_daily_empty(self):
        with (
            mock.patch.object(self.remctl, "open_db", return_value=object()),
            mock.patch.object(self.remctl, "q_overdue_daily", return_value=[]),
            mock.patch.object(self.remctl, "cmd_edit") as edit,
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            self.remctl.cmd_reset_daily(SimpleNamespace(json=False))
        edit.assert_not_called()
        self.assertIn("No overdue daily reminders", stdout.getvalue())

    def test_cmd_reset_daily_continues_after_edit_error(self):
        now = datetime(2026, 9, 22, 8, 0)
        due = self.remctl.to_ts(datetime(2026, 9, 20))
        rows = [
            self._row(Z_PK=1, ZTITLE="A", ZALLDAY=1, ZDISPLAYDATEDATE=due),
            self._row(Z_PK=2, ZTITLE="B", ZALLDAY=1, ZDISPLAYDATEDATE=due),
        ]

        def fake_edit(args):
            if args.id == 1:
                print("Error: boom", file=sys.stderr)
                raise SystemExit(1)
            print(json.dumps({"status": "updated", "id": 2}))

        FakeDateTime = type("FakeDateTime", (datetime,), {"now": staticmethod(lambda tz=None: now)})
        with (
            mock.patch.object(self.remctl, "open_db", return_value=object()),
            mock.patch.object(self.remctl, "q_overdue_daily", return_value=rows),
            mock.patch.object(self.remctl, "datetime", FakeDateTime),
            mock.patch.object(self.remctl, "cmd_edit", side_effect=fake_edit),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as raised,
        ):
            self.remctl.cmd_reset_daily(SimpleNamespace(json=True))
        self.assertEqual(raised.exception.code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["updated"], 1)
        self.assertEqual(payload["errors"], 1)

    def test_launchd_plist_runs_reset_daily_at_3am(self):
        plist = self.remctl.reset_daily_launchd_plist("/tmp/bin/remctl")
        self.assertEqual(plist["Label"], "com.remctl.reset-daily")
        self.assertEqual(plist["ProgramArguments"], ["/tmp/bin/remctl", "reset-daily", "--json"])
        self.assertEqual(plist["StartCalendarInterval"], {"Hour": 3, "Minute": 0})
        self.assertFalse(plist["RunAtLoad"])
        self.assertIn("/tmp/bin", plist["EnvironmentVariables"]["PATH"])

    def test_reset_daily_install_writes_plist_without_launchctl(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            config = Path(tmp) / "config"
            binary = Path(tmp) / "bin" / "remctl"
            binary.parent.mkdir(parents=True)
            binary.write_text("#!/bin/sh\n")
            home.mkdir()
            with (
                mock.patch.object(self.remctl, "installed_cli_path", return_value=binary),
                mock.patch.object(self.remctl, "CONFIG_DIR", config),
                mock.patch.object(self.remctl.Path, "home", return_value=home),
                mock.patch.object(self.remctl.shutil, "which", return_value=None),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
            ):
                self.remctl.cmd_reset_daily_install(SimpleNamespace(json=True))
            plist_path = home / "Library" / "LaunchAgents" / "com.remctl.reset-daily.plist"
            self.assertTrue(plist_path.exists())
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["plist"], str(plist_path))
            self.assertEqual(payload["hour"], 3)
            self.assertFalse(payload["loaded"])
            with open(plist_path, "rb") as handle:
                data = self.remctl.plistlib.load(handle)
            self.assertEqual(data["StartCalendarInterval"]["Hour"], 3)
            self.assertEqual(data["ProgramArguments"][1], "reset-daily")

    def test_parser_registers_reset_daily_commands(self):
        parser, sub = self.remctl.build_parser()
        for name in ("reset-daily", "reset-daily-install", "reset-daily-uninstall"):
            self.assertIn(name, sub.choices)
        args = self.remctl.parse_cli_args(parser, sub, ["reset-daily", "--json"])
        self.assertTrue(args.json)
        self.assertEqual(args.cmd, "reset-daily")


if __name__ == "__main__":
    unittest.main()
