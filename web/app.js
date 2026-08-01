(() => {
  "use strict";

  const textarea      = document.getElementById("email-text");
  const charCount      = document.getElementById("char-count");
  const sweep          = document.getElementById("sweep");
  const analyzeBtn     = document.getElementById("analyze-btn");
  const errorMsg       = document.getElementById("error-msg");
  const needle          = document.getElementById("needle");
  const verdictLabel    = document.getElementById("verdict-label");
  const verdictConfidence = document.getElementById("verdict-confidence");
  const logList         = document.getElementById("log-list");
  const logEmpty        = document.getElementById("log-empty");
  const clearLogBtn     = document.getElementById("clear-log");
  const gaugeTicksGroup = document.getElementById("gauge-ticks");

  const SAMPLES = {
    urgent:   "URGENT : votre compte a été suspendu. Cliquez ici immédiatement pour vérifier votre identité, sans quoi l'accès sera bloqué sous 24 heures : http://secure-verif-account.com/login",
    prize:    "Félicitations ! Vous avez gagné une carte cadeau de 1000€. Cliquez sur ce lien dès maintenant pour la réclamer avant expiration de l'offre.",
    meeting:  "Salut, petit rappel : notre point d'équipe hebdomadaire est déplacé à 15h demain. Dis-moi si ça te convient toujours.",
    delivery: "Merci pour votre commande ! Votre colis a été expédié et devrait arriver sous 3 à 5 jours ouvrés. Vous pouvez suivre la livraison depuis votre compte.",
  };

  /* ---------------------------------------------------------------------
   * Compteur de caractères
   * ------------------------------------------------------------------- */
  function updateCharCount() {
    charCount.textContent = `${textarea.value.length} / 5000`;
  }
  textarea.addEventListener("input", updateCharCount);
  updateCharCount();

  /* ---------------------------------------------------------------------
   * Chips d'exemples rapides
   * ------------------------------------------------------------------- */
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const key = chip.dataset.sample;
      textarea.value = SAMPLES[key] || "";
      updateCharCount();
      textarea.focus();
    });
  });

  /* ---------------------------------------------------------------------
   * Jauge : graduations générées une fois au chargement
   * ------------------------------------------------------------------- */
  function buildTicks() {
    const cx = 150, cy = 150, rOuter = 128, rInner = 118;
    const angles = [180, 135, 90, 45, 0]; // degrés, convention mathématique standard
    angles.forEach((deg) => {
      const rad = (deg * Math.PI) / 180;
      const x1 = cx + rOuter * Math.cos(rad);
      const y1 = cy - rOuter * Math.sin(rad);
      const x2 = cx + rInner * Math.cos(rad);
      const y2 = cy - rInner * Math.sin(rad);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", x1.toFixed(1));
      line.setAttribute("y1", y1.toFixed(1));
      line.setAttribute("x2", x2.toFixed(1));
      line.setAttribute("y2", y2.toFixed(1));
      line.setAttribute("class", "gauge-tick");
      gaugeTicksGroup.appendChild(line);
    });
  }
  buildTicks();

  /* Positionne l'aiguille. score in [0, 1] : 0 = légitime certain,
     1 = phishing certain, 0.5 = incertain (aiguille au centre, vers le haut). */
  function setNeedle(score) {
    const cssDeg = score * 180 - 90;
    needle.style.transform = `rotate(${cssDeg}deg)`;
  }

  /* ---------------------------------------------------------------------
   * Statistiques du moteur (chargées une fois au démarrage)
   * ------------------------------------------------------------------- */
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      if (!res.ok) return;
      const s = await res.json();
      document.getElementById("stat-vocab").textContent = `${s.vocab_size} mots`;
      document.getElementById("stat-dataset").textContent =
        `${s.dataset_size} (${s.phishing_count}/${s.legit_count})`;
      document.getElementById("stat-accuracy").textContent = `${(s.test_accuracy * 100).toFixed(1)} %`;
      document.getElementById("stat-f1").textContent = `${(s.test_f1 * 100).toFixed(1)} %`;
    } catch (e) {
      /* silencieux : les stats sont un bonus, pas un bloqueur */
    }
  }
  loadStats();

  /* ---------------------------------------------------------------------
   * Journal de session (client-side, ne persiste pas)
   * ------------------------------------------------------------------- */
  function addLogEntry(text, verdict, confidence) {
    logEmpty.hidden = true;
    const li = document.createElement("li");
    li.className = "log__row";

    const time = new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    const snippet = text.length > 70 ? text.slice(0, 70) + "…" : text;
    const isDanger = verdict === "phishing";

    li.innerHTML = `
      <span class="log__time">${time}</span>
      <span class="log__snippet" title="${escapeHtml(text)}">${escapeHtml(snippet)}</span>
      <span class="log__tag ${isDanger ? "log__tag--danger" : "log__tag--safe"}">
        ${isDanger ? "PHISHING" : "LÉGITIME"}
      </span>
      <span class="log__confidence">${(confidence * 100).toFixed(0)} %</span>
    `;
    logList.prepend(li);
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  clearLogBtn.addEventListener("click", () => {
    logList.querySelectorAll(".log__row").forEach((row) => row.remove());
    logEmpty.hidden = false;
  });

  /* ---------------------------------------------------------------------
   * Analyse
   * ------------------------------------------------------------------- */
  function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.hidden = false;
  }
  function hideError() {
    errorMsg.hidden = true;
  }

  function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.classList.toggle("is-loading", isLoading);
    sweep.classList.toggle("is-active", isLoading);
  }

  async function analyze() {
    const text = textarea.value.trim();
    hideError();

    if (!text) {
      showError("Colle d'abord le texte d'un email à analyser.");
      return;
    }

    setLoading(true);
    const minDelay = new Promise((resolve) => setTimeout(resolve, 500)); // pour que le scan soit perceptible

    try {
      const [res] = await Promise.all([
        fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        }),
        minDelay,
      ]);

      const data = await res.json();
      if (!res.ok) {
        showError(data.error || "Une erreur est survenue.");
        return;
      }

      const { verdict, confidence } = data;
      const isDanger = verdict === "phishing";

      // score pour l'aiguille : direction selon le verdict, amplitude selon la confiance
      const score = isDanger ? 0.5 + confidence / 2 : 0.5 - confidence / 2;
      setNeedle(score);

      verdictLabel.textContent = isDanger ? "Phishing détecté ⚠" : "Message légitime ✓";
      verdictLabel.classList.toggle("is-danger", isDanger);
      verdictLabel.classList.toggle("is-safe", !isDanger);
      verdictConfidence.textContent = `${(confidence * 100).toFixed(1)} %`;

      addLogEntry(text, verdict, confidence);
    } catch (e) {
      showError("Impossible de contacter le serveur d'analyse. Est-il bien lancé (python3 server.py) ?");
    } finally {
      setLoading(false);
    }
  }

  analyzeBtn.addEventListener("click", analyze);
  textarea.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") analyze();
  });
})();
