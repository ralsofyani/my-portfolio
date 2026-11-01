/* Rawan · Portfolio — small, dependency-free interactions. */
(() => {
  "use strict";

  const root = document.documentElement;
  const I18N = JSON.parse(document.getElementById("i18n-data").textContent);
  const RTL = new Set(["ar"]);
  let lang = root.lang;

  const lookup = (obj, path) => path.split(".").reduce((o, k) => (o == null ? o : o[k]), obj);
  const t = (path) => lookup(I18N[lang], path);
  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
  };

  /* ---------- Language switch (no reload) ---------- */
  function applyLanguage(next, { animate = true } = {}) {
    if (!I18N[next] || next === lang) return;
    const swap = () => {
      lang = next;
      root.lang = next;
      root.dir = RTL.has(next) ? "rtl" : "ltr";
      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const v = t(el.dataset.i18n);
        if (typeof v === "string") el.textContent = v;
      });
      document.querySelectorAll("[data-i18n-alt]").forEach((el) => { el.alt = t(el.dataset.i18nAlt) ?? el.alt; });
      document.querySelectorAll("[data-i18n-aria]").forEach((el) => el.setAttribute("aria-label", t(el.dataset.i18nAria) ?? ""));
      document.querySelectorAll("[data-i18n-content]").forEach((el) => el.setAttribute("content", t(el.dataset.i18nContent) ?? ""));
      document.dispatchEvent(new CustomEvent("langchange"));
      store.set("lang", next);
      const url = new URL(location.href);
      url.searchParams.set("lang", next);
      history.replaceState(null, "", url);
    };
    if (!animate) return swap();
    document.body.classList.add("is-switching");
    setTimeout(() => { swap(); document.body.classList.remove("is-switching"); }, 200);
  }

  document.getElementById("lang-toggle").addEventListener("click", () => applyLanguage(lang === "ar" ? "en" : "ar"));

  // ?lang=… in the URL wins (also needed on the static build); otherwise respect a remembered choice.
  const urlLang = new URLSearchParams(location.search).get("lang");
  const saved = store.get("lang");
  if (urlLang && I18N[urlLang]) { if (urlLang !== lang) applyLanguage(urlLang, { animate: false }); }
  else if (saved && saved !== lang) applyLanguage(saved, { animate: false });

  /* ---------- Mobile menu ---------- */
  const menuBtn = document.getElementById("menu-toggle");
  const links = document.getElementById("nav-links");
  menuBtn.addEventListener("click", () => {
    const open = links.classList.toggle("is-open");
    menuBtn.setAttribute("aria-expanded", String(open));
  });
  links.addEventListener("click", (e) => {
    if (e.target.closest("a")) { links.classList.remove("is-open"); menuBtn.setAttribute("aria-expanded", "false"); }
  });

  /* ---------- Reveal on scroll + meters ---------- */
  const revealer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-in");
      entry.target.querySelectorAll(".meter").forEach((m) => m.classList.add("is-in"));
      revealer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  document.querySelectorAll(".reveal").forEach((el, i) => {
    el.style.transitionDelay = `${(i % 4) * 70}ms`;
    revealer.observe(el);
  });

  /* ---------- Active nav link ---------- */
  const navMap = new Map([...links.querySelectorAll("a")].map((a) => [a.hash.slice(1), a]));
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      navMap.forEach((a) => a.classList.remove("is-current"));
      navMap.get(entry.target.id)?.classList.add("is-current");
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  document.querySelectorAll("main section[id]").forEach((s) => spy.observe(s));

  const toTop = document.querySelector(".to-top");
  addEventListener("scroll", () => toTop.classList.toggle("is-visible", scrollY > 700), { passive: true });

  /* ---------- Project filters ---------- */
  const chips = document.querySelectorAll(".chip[data-filter]");
  const cards = document.querySelectorAll(".project");
  const empty = document.querySelector(".empty-note");
  chips.forEach((chip) => chip.addEventListener("click", () => {
    chips.forEach((c) => c.classList.toggle("is-active", c === chip));
    let shown = 0;
    cards.forEach((card) => {
      const show = chip.dataset.filter === "all" || card.dataset.status === chip.dataset.filter;
      card.classList.toggle("is-hidden", !show);
      if (show) { shown++; card.classList.add("is-in"); }
    });
    empty.hidden = shown > 0;
  }));

  /* ---------- What should I explore today? ----------
     Ideas come from FastAPI (GET /api/learning-ideas) once; after that every
     click is local. We walk through a shuffled order of all ideas before any
     repeats, and remember the cycle in this browser so a refresh doesn't reset it. */
  const ideaCard = document.getElementById("idea-card");
  if (ideaCard) {
    const KEY = "learning-ideas-cycle";
    const nextBtn = document.getElementById("idea-next");
    const out = {
      topic: document.getElementById("idea-topic"),
      title: document.getElementById("idea-title"),
      text: document.getElementById("idea-text"),
      count: document.getElementById("idea-count"),
    };
    let byId = {};
    let cycle = null; // { order: [ids...], pos: n }

    const shuffle = (ids, avoidFirst) => {
      const a = [...ids];
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      // never show the same idea twice in a row across a reshuffle
      if (avoidFirst && a.length > 1 && a[0] === avoidFirst) [a[0], a[1]] = [a[1], a[0]];
      return a;
    };
    const save = () => store.set(KEY, JSON.stringify(cycle));
    const restore = () => { try { return JSON.parse(store.get(KEY)); } catch { return null; } };

    const render = (animate) => {
      const idea = byId[cycle.order[cycle.pos]];
      if (!idea) return;
      const apply = () => {
        out.topic.textContent = idea.topic[lang];
        out.title.textContent = idea[lang].title;
        out.text.textContent = idea[lang].text;
        out.count.textContent = (t("ideas.counter") || "{n} / {total}")
          .replace("{n}", cycle.pos + 1).replace("{total}", cycle.order.length);
      };
      if (!animate) return apply();
      ideaCard.classList.add("is-changing");
      setTimeout(() => { apply(); ideaCard.classList.remove("is-changing"); }, 180);
    };

    const next = () => {
      cycle.pos += 1;
      if (cycle.pos >= cycle.order.length) {
        const last = cycle.order[cycle.order.length - 1];
        cycle = { order: shuffle(Object.keys(byId), last), pos: 0 };
      }
      save();
      render(true);
    };

    fetch(root.dataset.ideasUrl || "/api/learning-ideas")
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data) => {
        byId = Object.fromEntries(data.ideas.map((i) => [i.id, i]));
        const ids = Object.keys(byId);
        const saved = restore();
        const valid = saved && Array.isArray(saved.order) && saved.order.length === ids.length
          && saved.order.every((id) => byId[id]) && Number.isInteger(saved.pos)
          && saved.pos >= 0 && saved.pos < ids.length;
        cycle = valid ? saved : { order: shuffle(ids), pos: 0 };
        save();
        render(false);
        nextBtn.disabled = false;
      })
      .catch(() => { nextBtn.disabled = true; });

    nextBtn.addEventListener("click", next);
    document.addEventListener("langchange", () => { if (cycle) render(false); });
  }

  /* ---------- Copy email ---------- */
  const copyBtn = document.getElementById("copy-email");
  copyBtn?.addEventListener("click", async () => {
    const label = copyBtn.querySelector("span");
    try { await navigator.clipboard.writeText(copyBtn.dataset.email); } catch { /* clipboard blocked */ }
    label.textContent = t("contact.copied");
    setTimeout(() => (label.textContent = t("contact.copy_email")), 1800);
  });
})();
