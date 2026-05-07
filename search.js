/* TJIP Phase 02 — site search.
 *
 * Reads search-index.json (built by scripts/build_index.py) and powers the
 * dropdown attached to .site-search-input in the nav. Word-boundary matching
 * keeps queries like "raft" from also matching "Craft".
 */
(function () {
  const base = document.body.dataset.base || "";

  // Field weights — higher means a hit there outranks a hit elsewhere.
  const FIELDS = [
    ["title", 10],
    ["h1", 8],
    ["headings", 4],
    ["deck", 2],
    ["lede", 2],
    ["theme", 2],
    ["body", 1],
  ];

  let index = null;
  let indexLoad = null;

  function loadIndex() {
    if (index) return Promise.resolve(index);
    if (indexLoad) return indexLoad;
    indexLoad = fetch(base + "search-index.json")
      .then((r) => r.json())
      .then((data) => {
        index = data;
        return data;
      });
    return indexLoad;
  }

  function escapeRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function escapeHtml(s) {
    return s.replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  }

  function fieldText(rec, key) {
    const v = rec[key];
    return Array.isArray(v) ? v.join(" ") : v || "";
  }

  function tokenize(query) {
    return query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  }

  function buildRegexes(tokens, flags) {
    return tokens.map((t) => new RegExp("\\b" + escapeRegex(t), flags));
  }

  // Score: every query token must match somewhere in the record. A token's
  // contribution is the weight of the highest-ranked field where it hit.
  function search(query) {
    const tokens = tokenize(query);
    if (tokens.length === 0 || !index) return [];
    const regexes = buildRegexes(tokens, "i");

    const hits = [];
    for (const rec of index) {
      let score = 0;
      let matched = 0;
      for (const re of regexes) {
        let best = 0;
        for (const [key, weight] of FIELDS) {
          if (weight > best && re.test(fieldText(rec, key))) {
            best = weight;
          }
        }
        if (best > 0) {
          matched++;
          score += best;
        }
      }
      if (matched === regexes.length) hits.push({ rec, score });
    }
    hits.sort((a, b) => b.score - a.score);
    return hits.slice(0, 8);
  }

  // Pick a window of text around the first matched token, biased toward body
  // > lede > deck so technical-term searches show the actual paragraph.
  function snippetFor(rec, regexes) {
    for (const key of ["body", "lede", "deck", "h1", "title"]) {
      const text = fieldText(rec, key);
      for (const re of regexes) {
        const m = text.match(re);
        if (m) {
          const start = Math.max(0, m.index - 60);
          const end = Math.min(text.length, m.index + m[0].length + 90);
          let s = text.slice(start, end);
          if (start > 0) s = "…" + s;
          if (end < text.length) s = s + "…";
          return s;
        }
      }
    }
    return rec.deck || "";
  }

  function highlight(text, tokens) {
    const escaped = escapeHtml(text);
    let out = escaped;
    for (const t of tokens) {
      const re = new RegExp("\\b" + escapeRegex(t), "gi");
      out = out.replace(re, (m) => "<mark>" + m + "</mark>");
    }
    return out;
  }

  function init() {
    const input = document.querySelector(".site-search-input");
    const dropdown = document.querySelector(".site-search-results");
    if (!input || !dropdown) return;

    let active = -1;

    function render(query) {
      if (!query.trim()) {
        dropdown.innerHTML = "";
        dropdown.hidden = true;
        active = -1;
        return;
      }
      const hits = search(query);
      if (hits.length === 0) {
        dropdown.innerHTML = '<div class="site-search-empty">No matches.</div>';
        dropdown.hidden = false;
        active = -1;
        return;
      }
      const tokens = tokenize(query);
      const regexes = buildRegexes(tokens, "i");
      dropdown.innerHTML = hits
        .map(({ rec }, i) => {
          const snippet = snippetFor(rec, regexes);
          return (
            '<a class="site-search-result' +
            (i === 0 ? " is-active" : "") +
            '"' +
            ' href="' +
            escapeHtml(base + rec.url) +
            '" data-index="' +
            i +
            '">' +
            '<div class="result-row">' +
            '<span class="result-title">' +
            highlight(rec.title, tokens) +
            "</span>" +
            '<span class="result-theme">' +
            escapeHtml(rec.theme) +
            "</span>" +
            "</div>" +
            '<div class="result-snippet">' +
            highlight(snippet, tokens) +
            "</div>" +
            "</a>"
          );
        })
        .join("");
      dropdown.hidden = false;
      active = 0;
    }

    function move(delta) {
      const items = dropdown.querySelectorAll(".site-search-result");
      if (items.length === 0) return;
      if (active >= 0) items[active].classList.remove("is-active");
      active = (active + delta + items.length) % items.length;
      items[active].classList.add("is-active");
      items[active].scrollIntoView({ block: "nearest" });
    }

    input.addEventListener("focus", () => {
      loadIndex().then(() => {
        if (input.value.trim()) render(input.value);
      });
    });

    input.addEventListener("input", () => {
      if (!index) loadIndex().then(() => render(input.value));
      else render(input.value);
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        move(1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        move(-1);
      } else if (e.key === "Enter") {
        const items = dropdown.querySelectorAll(".site-search-result");
        if (active >= 0 && items[active]) {
          e.preventDefault();
          window.location.href = items[active].getAttribute("href");
        }
      } else if (e.key === "Escape") {
        dropdown.hidden = true;
        input.blur();
      }
    });

    dropdown.addEventListener("mousemove", (e) => {
      const item = e.target.closest(".site-search-result");
      if (!item) return;
      const idx = Number(item.dataset.index);
      if (idx === active) return;
      const items = dropdown.querySelectorAll(".site-search-result");
      if (active >= 0) items[active].classList.remove("is-active");
      active = idx;
      item.classList.add("is-active");
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".site-search")) dropdown.hidden = true;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
