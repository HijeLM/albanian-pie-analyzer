import { useState, useEffect, useRef, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Language flag/abbreviation map
const LANG_ABBR = {
  Latin: "LAT", Greek: "GRC", Sanskrit: "SKT", English: "ENG",
  German: "DEU", French: "FRA", Russian: "RUS", Spanish: "SPA",
  Gothic: "GOT", "Old Irish": "OIR", Welsh: "CYM", Armenian: "HYE",
  Lithuanian: "LIT", Latvian: "LAV", Slavic: "SLV", Celtic: "CEL",
  Avestan: "AVE", "Old Norse": "NON", Polish: "POL", Danish: "DAN",
  Norwegian: "NOR",
};

function ScoreDisplay({ score, label }) {
  const s = Math.round(score);
  const tier =
    s >= 90 ? { color: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0" }
    : s >= 70 ? { color: "#d97706", bg: "#fffbeb", border: "#fde68a" }
    : s >= 40 ? { color: "#ea580c", bg: "#fff7ed", border: "#fed7aa" }
    : { color: "#dc2626", bg: "#fef2f2", border: "#fecaca" };

  return (
    <div className="score-display">
      <div className="score-number" style={{ color: tier.color }}>
        {s}<span className="score-denom">/100</span>
      </div>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${s}%`, background: tier.color }} />
      </div>
      <div className="score-label-pill" style={{ color: tier.color, background: tier.bg, borderColor: tier.border }}>
        {label}
      </div>
    </div>
  );
}

function CognateTag({ lang, word, meaning }) {
  const abbr = LANG_ABBR[lang] || lang.slice(0, 3).toUpperCase();
  return (
    <div className="cognate-tag" title={meaning ? `${word}: ${meaning}` : word}>
      <span className="cognate-lang">{abbr}</span>
      <span className="cognate-word">{word}</span>
    </div>
  );
}

function EvolutionChain({ evolutions }) {
  if (!evolutions || evolutions.length === 0) return null;
  return (
    <div className="evolution-chain">
      {evolutions.flatMap((ev, i) => {
        const items = [
          <div key={`step-${ev.stage}-${ev.form}`} className="evo-step">
            <div className="evo-stage">{ev.stage}</div>
            <div className="evo-form">{ev.form}</div>
          </div>,
        ];
        if (i < evolutions.length - 1)
          items.push(<div key={`arrow-${i}`} className="evo-arrow">→</div>);
        return items;
      })}
    </div>
  );
}

function generateShareCard(result) {
  const W = 1080, H = 1080;
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext("2d");

  // Background
  const grad = ctx.createLinearGradient(0, 0, W, H);
  grad.addColorStop(0, "#f8f8f6");
  grad.addColorStop(1, "#ededf2");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  // Accent bar top
  ctx.fillStyle = "#5b5bd6";
  ctx.fillRect(0, 0, W, 8);

  // Logo box
  ctx.fillStyle = "#1c1c1e";
  roundRect(ctx, 60, 60, 80, 80, 18);
  ctx.fill();
  ctx.fillStyle = "#fff";
  ctx.font = "500 22px 'Courier New', monospace";
  ctx.textAlign = "left";
  ctx.fillText("Alb", 82, 110);

  // App name
  ctx.fillStyle = "#9b9b95";
  ctx.font = "400 26px sans-serif";
  ctx.textAlign = "left";
  ctx.fillText("Albanian PIE Analyzer", 160, 108);

  // Word — large serif
  ctx.fillStyle = "#1c1c1e";
  ctx.textAlign = "center";
  const wordSize = result.word.length > 10 ? 110 : 140;
  ctx.font = `600 ${wordSize}px Georgia, serif`;
  ctx.fillText(result.word, W / 2, 340);

  // POS badge
  if (result.type && result.type !== "unknown") {
    ctx.font = "500 28px sans-serif";
    ctx.fillStyle = "#9b9b95";
    ctx.fillText(result.type.toUpperCase(), W / 2, 400);
  }

  // Meaning
  if (result.meaning) {
    ctx.font = "italic 48px Georgia, serif";
    ctx.fillStyle = "#3a3a3c";
    const meaning = result.meaning.length > 40
      ? result.meaning.slice(0, 40) + "…"
      : result.meaning;
    ctx.fillText(`"${meaning}"`, W / 2, 490);
  }

  // Divider
  ctx.strokeStyle = "#e4e4e0";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(80, 540); ctx.lineTo(W - 80, 540);
  ctx.stroke();

  // Evolution chain — PIE → Proto-Albanian → Albanian
  const evos = (result.evolutions || []);
  if (evos.length > 0) {
    ctx.textAlign = "center";
    ctx.font = "500 22px sans-serif";
    ctx.fillStyle = "#9b9b95";
    ctx.fillText("EVOLUTION", W / 2, 590);

    const stepW = 240;
    const arrowW = 60;
    const totalW = evos.length * stepW + (evos.length - 1) * arrowW;
    const startX = (W - totalW) / 2;

    evos.forEach((ev, i) => {
      const x = startX + i * (stepW + arrowW);
      const cx = x + stepW / 2;

      // Stage label
      ctx.font = "500 18px sans-serif";
      ctx.fillStyle = "#9b9b95";
      ctx.textAlign = "center";
      const stageLabel = ev.stage === "Proto-Albanian" ? "PROTO-ALB" : ev.stage.toUpperCase();
      ctx.fillText(stageLabel, cx, 630);

      // Box
      ctx.fillStyle = "#f0f0ee";
      roundRect(ctx, x, 642, stepW, 52, 10);
      ctx.fill();
      ctx.strokeStyle = "#e4e4e0";
      ctx.lineWidth = 1.5;
      roundRect(ctx, x, 642, stepW, 52, 10);
      ctx.stroke();

      // Form text
      ctx.font = "500 26px 'Courier New', monospace";
      ctx.fillStyle = i === evos.length - 1 ? "#1c1c1e" : "#5b5bd6";
      const form = ev.form.length > 14 ? ev.form.slice(0, 13) + "…" : ev.form;
      ctx.fillText(form, cx, 677);

      // Arrow
      if (i < evos.length - 1) {
        ctx.font = "400 36px sans-serif";
        ctx.fillStyle = "#ccc";
        ctx.fillText("→", x + stepW + arrowW / 2, 677);
      }
    });
  }

  // Second divider
  ctx.strokeStyle = "#e4e4e0";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(80, 730); ctx.lineTo(W - 80, 730);
  ctx.stroke();

  // PIE Root
  if (result.root) {
    ctx.textAlign = "left";
    ctx.font = "500 22px sans-serif";
    ctx.fillStyle = "#9b9b95";
    ctx.fillText("PIE ROOT", 80, 782);
    ctx.font = "500 36px 'Courier New', monospace";
    ctx.fillStyle = "#5b5bd6";
    ctx.fillText(result.root, 80, 826);
  }

  // Cognates
  const cogs = (result.cognates || []).slice(0, 3);
  if (cogs.length > 0) {
    ctx.textAlign = "right";
    ctx.font = "500 22px sans-serif";
    ctx.fillStyle = "#9b9b95";
    ctx.fillText("COGNATES", W - 80, 782);
    cogs.forEach((c, i) => {
      const y = 822 + i * 46;
      const abbr = (c.language || "").slice(0, 3).toUpperCase();
      ctx.fillStyle = "#f0f0ee";
      roundRect(ctx, W - 320, y - 26, 62, 32, 7);
      ctx.fill();
      ctx.font = "600 16px sans-serif";
      ctx.fillStyle = "#9b9b95";
      ctx.textAlign = "center";
      ctx.fillText(abbr, W - 289, y - 4);
      ctx.font = "500 24px 'Courier New', monospace";
      ctx.fillStyle = "#1c1c1e";
      ctx.textAlign = "right";
      ctx.fillText(c.word, W - 80, y - 2);
    });
  }

  // Sources line
  const sources = (result.sources || []).join(" · ");
  if (sources) {
    ctx.textAlign = "left";
    ctx.font = "400 22px sans-serif";
    ctx.fillStyle = "#bcbcb8";
    ctx.fillText(`Source: ${sources}`, 80, 970);
  }

  // Bottom branding
  ctx.fillStyle = "#5b5bd6";
  ctx.fillRect(0, H - 8, W, 8);

  return canvas.toDataURL("image/png");
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function ShareModal({ result, onClose }) {
  const [copied, setCopied] = useState(false);
  const imgUrl = generateShareCard(result);

  const xText = [
    `The Albanian word "${result.word}" (${result.meaning || ""}) traces back to PIE ${result.root || ""}`,
    result.cognates?.slice(0, 3).map(c => `${c.language}: ${c.word}`).join(" · ") || "",
    "#etymology #Albanian #linguistics",
  ].filter(Boolean).join("\n");

  const shareX = async () => {
    // On mobile: native share sheet (X, Instagram, WhatsApp…) with image + text
    if (navigator.canShare) {
      try {
        const blob = await (await fetch(imgUrl)).blob();
        const file = new File([blob], `${result.word}-etymology.png`, { type: "image/png" });
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], text: xText, title: `Albanian word: ${result.word}` });
          return;
        }
      } catch (e) {
        // user cancelled or not supported — fall through
      }
    }
    // Desktop fallback: open X intent with text only
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(xText)}`, "_blank");
  };

  const downloadInsta = () => {
    const a = document.createElement("a");
    a.href = imgUrl;
    a.download = `${result.word}-etymology.png`;
    a.click();
  };

  const copyText = () => {
    navigator.clipboard.writeText(xText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card share-modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>
        <h2 className="share-title">Share</h2>

        <img src={imgUrl} alt="Etymology card" className="share-preview" />

        <div className="share-actions">
          <button className="share-btn share-x" onClick={shareX}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
            Share on X / Instagram
          </button>
          <button className="share-btn share-insta" onClick={downloadInsta}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/>
              <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>
            </svg>
            Save for Instagram
          </button>
          <button className="share-btn share-copy" onClick={copyText}>
            {copied ? "Copied!" : "Copy text"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Modal({ result, onClose }) {
  const overlayRef = useRef(null);
  const [showShare, setShowShare] = useState(false);

  useEffect(() => {
    const handleKey = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose();
  };

  if (!result) return null;

  const isFound = result.found !== false;

  return (
    <>
    <div className="modal-overlay" ref={overlayRef} onClick={handleOverlayClick}>
      <div className="modal-card" role="dialog" aria-modal="true">
        <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>

        <div className="modal-header">
          <div className="modal-word">{result.word}</div>
          <div className="modal-header-row">
            {result.type && result.type !== "unknown" && (
              <div className="modal-pos">{result.type}</div>
            )}
            {isFound && (
              <button className="share-trigger" onClick={() => setShowShare(true)}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                  <polyline points="16 6 12 2 8 6"/>
                  <line x1="12" y1="2" x2="12" y2="15"/>
                </svg>
                Share
              </button>
            )}
          </div>
        </div>

        {!isFound ? (
          <div className="not-found-block">
            <div className="not-found-icon">⚠</div>
            <div className="not-found-msg">{result.message || "Word not found in database."}</div>
            <ScoreDisplay score={result.score} label={result.label} />
          </div>
        ) : (
          <div className="modal-body">
            {result.meaning && (
              <section className="modal-section">
                <div className="section-label">Meaning</div>
                <div className="meaning-text">{result.meaning}</div>
              </section>
            )}

            {result.root && (
              <section className="modal-section">
                <div className="section-label">PIE Root</div>
                <div className="pie-root">{result.root}</div>
              </section>
            )}

            {result.evolutions && result.evolutions.length > 0 && (
              <section className="modal-section">
                <div className="section-label">Evolution</div>
                <EvolutionChain evolutions={result.evolutions} />
              </section>
            )}

            {result.cognates && result.cognates.length > 0 && (
              <section className="modal-section">
                <div className="section-label">Cognates</div>
                <div className="cognates-grid">
                  {result.cognates.map((c) => (
                    <CognateTag key={`${c.language}-${c.word}`} lang={c.language} word={c.word} meaning={c.meaning} />
                  ))}
                </div>
              </section>
            )}

            <section className="modal-section score-section">
              <div className="section-label">Authenticity</div>
              <div className="score-row">
                <ScoreDisplay score={result.score} label={result.label} />
                <div className="score-meta">
                  {result.source_count > 0 && (
                    <div className="meta-line">
                      <span className="meta-key">Sources</span>
                      <span className="meta-val">{result.source_count}</span>
                    </div>
                  )}
                  {result.sources && result.sources.length > 0 && (
                    <div className="meta-line sources-list">
                      {result.sources.map((s) => (
                        <span key={s} className="source-badge">{s}</span>
                      ))}
                    </div>
                  )}
                  {result.notes && (
                    <div className="notes-text">{result.notes}</div>
                  )}
                </div>
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
    {showShare && <ShareModal result={result} onClose={() => setShowShare(false)} />}
    </>
  );
}

function SuggestionPill({ word, onClick }) {
  return (
    <button className="suggestion-pill" onClick={() => onClick(word)}>
      {word}
    </button>
  );
}

const EXAMPLE_WORDS = ["ujk", "diell", "dy", "pesë", "ujë", "kalë", "zemër", "gjak", "mbret", "zot"];

function DictModal({ onClose, onSelect }) {
  const [filter, setFilter] = useState("");
  const [sources, setSources] = useState([]);
  const [activeSource, setActiveSource] = useState(null);
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/sources`)
      .then(r => r.json())
      .then(setSources)
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const url = activeSource
      ? `${API_BASE}/words?limit=500&source_id=${activeSource}`
      : `${API_BASE}/words?limit=500`;
    fetch(url)
      .then(r => r.json())
      .then(data => { setWords(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [activeSource]);

  const filteredWords = words.filter(w =>
    w.word.toLowerCase().includes(filter.toLowerCase()) ||
    (w.meaning && w.meaning.toLowerCase().includes(filter.toLowerCase()))
  );

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card dict-modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>
        <h2 className="dict-title">Albanian Dictionary</h2>

        <div className="source-tabs">
          <button
            className={`source-tab ${activeSource === null ? "active" : ""}`}
            onClick={() => setActiveSource(null)}
          >
            All
          </button>
          {sources.map(s => (
            <button
              key={s.id}
              className={`source-tab ${activeSource === s.id ? "active" : ""}`}
              onClick={() => setActiveSource(s.id)}
            >
              {s.name}
            </button>
          ))}
        </div>

        <input
          type="text"
          className="dict-search"
          placeholder="Search words or meanings..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />

        <div className="dict-list">
          {loading ? (
            <div className="dict-loading">Loading…</div>
          ) : filteredWords.length === 0 ? (
            <div className="dict-loading">No words found.</div>
          ) : filteredWords.map(w => (
            <div key={w.word} className="dict-item" onClick={() => { onSelect(w.word); onClose(); }}>
              <div className="dict-word">{w.word}</div>
              <div className="dict-meaning">{w.meaning}</div>
              {w.root && <div className="dict-root">{w.root}</div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export default function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [showDict, setShowDict] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [suggActive, setSuggActive] = useState(-1);
  const [showSugg, setShowSugg] = useState(false);
  const inputRef = useRef(null);
  const debouncedQuery = useDebounce(query, 200);

  useEffect(() => {
    fetch(`${API_BASE}/stats`)
      .then(r => r.json())
      .then(setStats)
      .catch(() => {});
  }, []);


  useEffect(() => {
    if (!debouncedQuery.trim() || debouncedQuery.length < 1) {
      setSuggestions([]);
      setShowSugg(false);
      return;
    }
    fetch(`${API_BASE}/search?q=${encodeURIComponent(debouncedQuery.trim())}&limit=7`)
      .then(r => r.json())
      .then(data => {
        setSuggestions(data);
        setShowSugg(data.length > 0);
        setSuggActive(-1);
      })
      .catch(() => {});
  }, [debouncedQuery]);

  const analyze = useCallback(async (word) => {
    if (!word.trim()) return;
    setShowSugg(false);
    setSuggestions([]);
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/analyze/${encodeURIComponent(word.trim())}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError("Could not reach the API. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleKey = (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSuggActive(i => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSuggActive(i => Math.max(i - 1, -1));
    } else if (e.key === "Enter") {
      if (suggActive >= 0 && suggestions[suggActive]) {
        const w = suggestions[suggActive].word;
        setQuery(w);
        analyze(w);
      } else {
        analyze(query);
      }
    } else if (e.key === "Escape") {
      setShowSugg(false);
    }
  };

  const handleSuggestion = (word) => {
    setQuery(word);
    analyze(word);
    inputRef.current?.focus();
  };

  const handleSuggClick = (word) => {
    setQuery(word);
    analyze(word);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo-mark">Alb</div>
        <div className="header-text">
          <h1 className="app-title">Albanian PIE Analyzer</h1>
          <p className="app-subtitle">Trace Albanian words to their Proto-Indo-European origins</p>
          <button className="dict-btn" onClick={() => setShowDict(true)}>Dictionary</button>
        </div>
      </header>

      <main className="search-area">
        <div className="search-wrapper">
          <div className={`search-box ${loading ? "loading" : ""}`}>
            <span className="search-icon">
              {loading ? <span className="spinner" /> : "⌕"}
            </span>
            <input
              ref={inputRef}
              type="text"
              className="search-input"
              placeholder="Enter an Albanian word…"
              value={query}
              onChange={e => { setQuery(e.target.value); setShowSugg(true); }}
              onKeyDown={handleKey}
              onBlur={() => setTimeout(() => setShowSugg(false), 150)}
              onFocus={() => suggestions.length > 0 && setShowSugg(true)}
              autoFocus
              autoComplete="off"
              spellCheck={false}
              aria-autocomplete="list"
              aria-expanded={showSugg}
            />
            {query && (
              <button className="clear-btn" onClick={() => {
                setQuery("");
                setSuggestions([]);
                setShowSugg(false);
                inputRef.current?.focus();
              }}>×</button>
            )}
            <button
              className="search-btn"
              onClick={() => analyze(query)}
              disabled={!query.trim() || loading}
            >
              Analyze
            </button>
          </div>

          {showSugg && suggestions.length > 0 && (
            <ul className="autocomplete-dropdown" role="listbox">
              {suggestions.map((s, i) => (
                <li
                  key={s.word}
                  className={`autocomplete-item ${i === suggActive ? "active" : ""}`}
                  role="option"
                  aria-selected={i === suggActive}
                  onMouseDown={() => handleSuggClick(s.word)}
                  onMouseEnter={() => setSuggActive(i)}
                >
                  <span className="ac-word">{s.word}</span>
                  {s.meaning && <span className="ac-meaning">{s.meaning}</span>}
                </li>
              ))}
            </ul>
          )}
        </div>

        {error && <div className="error-msg">{error}</div>}

        <div className="suggestions">
          <span className="suggestions-label">Try:</span>
          {EXAMPLE_WORDS.map(w => (
            <SuggestionPill key={w} word={w} onClick={handleSuggestion} />
          ))}
        </div>

        {stats && (
          <div className="stats-bar">
            <span>{stats.words.toLocaleString()} words</span>
            <span className="stat-dot">·</span>
            <span>{stats.entries.toLocaleString()} entries</span>
            <span className="stat-dot">·</span>
            <span>{stats.sources} source{stats.sources !== 1 ? "s" : ""}</span>
          </div>
        )}
      </main>

      <footer className="app-footer">
        Based on Orel (1998) • Albanian etymological research tool
      </footer>

      {showDict && <DictModal onClose={() => setShowDict(false)} onSelect={handleSuggestion} />}
      {result && <Modal result={result} onClose={() => setResult(null)} />}
    </div>
  );
}
