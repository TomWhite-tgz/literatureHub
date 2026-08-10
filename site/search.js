(function () {
  "use strict";

  var input = document.getElementById("site-search-input");
  var results = document.getElementById("site-search-results");
  var status = document.getElementById("site-search-status");
  var clear = document.getElementById("site-search-clear");
  var documents = window.__SITE_SEARCH_INDEX__ || [];
  var timer;

  if (!input || !results || !status) return;

  function normalize(value) {
    return String(value || "").normalize("NFKC").toLocaleLowerCase().replace(/\s+/g, " ").trim();
  }

  function occurrences(haystack, needle, limit) {
    var count = 0;
    var position = 0;
    while (count < limit && (position = haystack.indexOf(needle, position)) !== -1) {
      count += 1;
      position += Math.max(needle.length, 1);
    }
    return count;
  }

  function rank(document, query, terms) {
    var title = normalize(document.title);
    var headings = normalize(document.headings);
    var path = normalize(document.category + " " + document.url);
    var text = normalize(document.text);
    var all = title + " " + headings + " " + path + " " + text;
    if (!terms.every(function (term) { return all.indexOf(term) !== -1; })) return 0;

    var score = 1;
    if (title === query) score += 180;
    if (title.indexOf(query) === 0) score += 110;
    if (title.indexOf(query) !== -1) score += 75;
    if (headings.indexOf(query) !== -1) score += 35;
    terms.forEach(function (term) {
      if (title.indexOf(term) !== -1) score += 45;
      if (headings.indexOf(term) !== -1) score += 22;
      if (path.indexOf(term) !== -1) score += 14;
      score += occurrences(text, term, 8) * 2;
    });
    return score;
  }

  function snippet(document, terms) {
    var source = document.text || document.headings || "";
    var normalized = normalize(source);
    var first = -1;
    terms.forEach(function (term) {
      var position = normalized.indexOf(term);
      if (position !== -1 && (first === -1 || position < first)) first = position;
    });
    var start = Math.max(0, first - 70);
    var end = Math.min(source.length, start + 210);
    return (start ? "…" : "") + source.slice(start, end).trim() + (end < source.length ? "…" : "");
  }

  function resultNode(document, terms) {
    var link = window.document.createElement("a");
    var heading = window.document.createElement("strong");
    var meta = window.document.createElement("span");
    var excerpt = window.document.createElement("span");
    link.className = "search-result";
    link.href = document.url;
    heading.textContent = document.title;
    meta.className = "search-result-meta";
    meta.textContent = document.category;
    excerpt.className = "search-result-snippet";
    excerpt.textContent = snippet(document, terms);
    link.appendChild(heading);
    link.appendChild(meta);
    link.appendChild(excerpt);
    return link;
  }

  function search() {
    var query = normalize(input.value);
    var terms = query.split(" ").filter(Boolean);
    results.replaceChildren();
    results.hidden = !query;
    clear.hidden = !query;

    if (!query) {
      status.textContent = "输入中文、英文标题或正文关键词；按 / 可快速聚焦。";
      return;
    }

    var matches = documents
      .map(function (document) { return { document: document, score: rank(document, query, terms) }; })
      .filter(function (entry) { return entry.score > 0; })
      .sort(function (left, right) {
        return right.score - left.score || left.document.title.localeCompare(right.document.title, "zh-CN");
      });

    status.textContent = matches.length
      ? "找到 " + matches.length + " 个页面" + (matches.length > 20 ? "，显示最相关的 20 个" : "")
      : "没有找到匹配页面，可以减少关键词后重试。";
    matches.slice(0, 20).forEach(function (entry) {
      results.appendChild(resultNode(entry.document, terms));
    });
  }

  input.addEventListener("input", function () {
    window.clearTimeout(timer);
    timer = window.setTimeout(search, 70);
  });
  input.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      input.value = "";
      search();
      input.blur();
    }
  });
  clear.addEventListener("click", function () {
    input.value = "";
    search();
    input.focus();
  });
  document.addEventListener("keydown", function (event) {
    var tag = document.activeElement && document.activeElement.tagName;
    if (event.key === "/" && tag !== "INPUT" && tag !== "TEXTAREA") {
      event.preventDefault();
      input.focus();
    }
  });

  search();
})();
