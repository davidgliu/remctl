import type { RecordData as D } from "./bridge";

// Generic CLI results also contain IDs and titles (lists, templates, receipts).
export function isReminder(value: any): boolean {
  return !!value && typeof value.id === "number" && typeof value.title === "string" && typeof value.completed === "boolean";
}

// Keep children beside a loaded parent. A filtered-out parent never hides a match.
export function arrangeReminders(items: D[], collapsed: number[] = []): D[] {
  const byId = new Map(items.map((item) => [item.id, item]));
  const children = new Map<number, D[]>();
  for (const item of items)
    if (byId.has(item.parentID) && item.parentID !== item.id)
      children.set(item.parentID, [
        ...(children.get(item.parentID) || []),
        item,
      ]);
  const result: D[] = [],
    seen = new Set<number>();
  const visit = (item: D, depth: number, section?: string) => {
    if (seen.has(item.id)) return;
    seen.add(item.id);
    result.push({ ...item, depth, groupSection: section || item.section });
    if (!collapsed.includes(item.id))
      for (const child of children.get(item.id) || [])
        visit(child, depth + 1, section || item.section);
    else {
      const mark = (child: D) => {
        if (seen.has(child.id)) return;
        seen.add(child.id);
        (children.get(child.id) || []).forEach(mark);
      };
      (children.get(item.id) || []).forEach(mark);
    }
  };
  items
    .filter((item) => !byId.has(item.parentID) || item.parentID === item.id)
    .forEach((item) => visit(item, 0));
  items.filter((item) => !seen.has(item.id)).forEach((item) => visit(item, 0));
  return result;
}

export function selectionRange(
  items: D[],
  anchor: number | null,
  target: number,
): number[] {
  const first = items.findIndex((item) => item.id === anchor),
    last = items.findIndex((item) => item.id === target);
  return first < 0 || last < 0
    ? [target]
    : items
        .slice(Math.min(first, last), Math.max(first, last) + 1)
        .map((item) => item.id);
}

export function rescheduledDue(item: D, date: string): string {
  return (
    date +
    (!item.allDay && item.dueDate ? " " + item.dueDate.slice(11, 16) : "")
  );
}

export function recurrenceText(rule?: D): string {
  if (!rule) return "";
  // Ordinal and terminating rules retain every field through the CLI's JSON grammar.
  const detailed = rule.daysOfWeekDetailed || [];
  const complex =
    detailed.some((day: D) => day.weekNumber) ||
    Object.keys(rule).some(
      (key) =>
        ![
          "frequency",
          "interval",
          "daysOfWeek",
          "daysOfWeekDetailed",
          "daysOfMonth",
        ].includes(key),
    );
  if (complex) return JSON.stringify(rule);
  const days = rule.daysOfWeek?.map(
    (day: number) => ["", "sun", "mon", "tue", "wed", "thu", "fri", "sat"][day],
  );
  return [
    rule.frequency,
    rule.interval > 1 ? "x" + rule.interval : "",
    (days || rule.daysOfMonth || []).join(","),
  ]
    .filter(Boolean)
    .join(" ");
}

export function earlyReminderText(value?: D): string {
  if (!value) return "";
  if (value.direction === "after") return value.label;
  return (
    String(value.value) +
    ({ 0: "m", 1: "h", 2: "d", 3: "w", 4: "mo" } as Record<number, string>)[
      value.unitCode
    ]
  );
}

/** Display known structured briefs without changing the underlying reminder note. */
export function notePresentation(notes: unknown): {text:string;label?:string;version?:string} {
  if (typeof notes !== 'string') return {text:''};
  try {
    const value = JSON.parse(notes);
    if (value && !Array.isArray(value) && typeof value.changelog === 'string' && (typeof value.app_url === 'string' || typeof value.name === 'string')) {
      return {text:value.changelog.replace(/\\n/g, '\n'), label:typeof value.labels === 'string' ? value.labels : undefined, version:typeof value.version === 'string' ? value.version : undefined};
    }
  } catch {}
  return {text:notes};
}

export function todaySection(item: Record<string, any>, date: string) {
  const due = item.displayDate || item.dueDate;
  if (!due) return 'Today';
  if (due.slice(0,10) < date) return 'Overdue';
  if (item.allDay) return 'Today';
  const hour = Number(due.slice(11,13));
  return hour < 12 ? 'Morning' : hour < 17 ? 'Afternoon' : 'Tonight';
}

// A negative pin date is Reminders' explicit hidden state; an absent date uses its default.
export function systemListVisible(smartLists: D[], view: string): boolean {
  const item = smartLists.find(list => list.kind === "built-in" && list.smartListType?.endsWith("." + view));
  return item ? Boolean(item.pinned) || item.pinnedDate == null : ["today", "scheduled", "flagged", "all"].includes(view);
}

export function pinnedSidebarLists(lists: D[], smartLists: D[]): D[] {
  return [...lists.filter(list => list.pinned && !list.isGroup).map(list => ({...list, sidebarKind: "list"})),
    ...smartLists.filter(list => list.pinned && list.kind === "custom").map(list => ({...list, sidebarKind: "smart"}))]
    .sort((a: D, b: D) => (a.pinnedDate ?? Number.MAX_SAFE_INTEGER) - (b.pinnedDate ?? Number.MAX_SAFE_INTEGER));
}

// A Smart List belongs to the same folder as an ordinary list. Missing folders
// fall back to the top level so a stale parent reference cannot hide a list.
export function sidebarLists(lists: D[], smartLists: D[]): D[] {
  const groups = new Set(lists.filter(list => list.isGroup).map(list => list.id));
  return [...lists.map(list => ({...list, sidebarKind: "list"})),
    ...smartLists.filter(list => list.kind === "custom").map(list => ({...list, title: list.name, sidebarKind: "smart"}))]
    .filter((list: D) => list.isGroup || !list.pinned)
    .map((list: D) => ({...list, parentListId: groups.has(list.parentListId) ? list.parentListId : undefined}));
}

export function sidebarKey(list: D): string {
  const kind = list.sidebarKind === "smart" || list.kind === "custom" ? "smart" : "list";
  return `${kind}:${list.objectUUID || list.id}`;
}

export function sidebarScope(list: D, lists: D[]): string {
  if (list.pinned && !list.isGroup) return "pinned";
  const parent = lists.find(group => group.isGroup && group.id === list.parentListId);
  return parent ? `group:${parent.objectUUID || parent.id}` : "top";
}

// Saved IDs stay ahead of new items. Removed IDs are ignored, and the default
// order remains stable until the user changes that particular sibling set.
export function orderSidebarItems(items: D[], order: string[] = []): D[] {
  const positions = new Map(order.map((key, index) => [key, index]));
  return [...items].sort((a, b) => (positions.get(sidebarKey(a)) ?? order.length) - (positions.get(sidebarKey(b)) ?? order.length));
}

export function moveSidebarItem(items: D[], key: string, direction: number): string[] {
  const keys = items.map(sidebarKey), index = keys.indexOf(key), target = index + direction;
  if (index >= 0 && target >= 0 && target < keys.length)
    [keys[index], keys[target]] = [keys[target], keys[index]];
  return keys;
}

// Fallback list colors, in Reminders' order, for lists that report none.
export const COLORS = ["#54b652", "#e9b92e", "#ef8d32", "#ed5e5e", "#ad72d8", "#5394ed"];
export function colorFor(list: D, index = 0): string {
  const c = list?.color;
  return typeof c === "string" && /^#[\da-f]{6}$/i.test(c)
    ? c
    : typeof c === "object" && c?.hex
      ? c.hex
      : COLORS[index % 6];
}
