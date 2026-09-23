const config = JSON.parse(document.getElementById("reader-config").textContent);
const rows = [...document.querySelectorAll(".utterance")],
  status = document.getElementById("playerStatus"),
  storageKey = config.storage_key,
  speakerOptions = config.speakers;
let player = null,
  playerReady = false,
  pendingSeek = null,
  playbackStopAt = null,
  corrections = {};
const playerPanel = document.getElementById("playerPanel"),
  playerSizeKey = config.player_size_key;
function setPlayerSize(size) {
  if (!["compact", "standard", "large"].includes(size)) size = "compact";
  playerPanel.classList.remove("compact", "large");
  if (size !== "standard") playerPanel.classList.add(size);
  document.querySelectorAll("[data-player-size]").forEach((button) =>
    button.classList.toggle("selected", button.dataset.playerSize === size)
  );
  localStorage.setItem(playerSizeKey, size);
}
document.querySelectorAll("[data-player-size]").forEach((button) =>
  button.onclick = () => setPlayerSize(button.dataset.playerSize)
);
setPlayerSize(localStorage.getItem(playerSizeKey) || "compact");
try {
  corrections = JSON.parse(localStorage.getItem(storageKey) || "{}");
} catch (e) {
  corrections = {};
}
function originalFor(row) {
  return {
    start: +row.dataset.start,
    end: +row.dataset.end,
    text: row.querySelector(".transcript-text").textContent,
    speaker: row.querySelector(".speaker").textContent.replace(/:$/, ""),
    note: row.querySelector(".editorial-note")?.textContent.replace(
      /^Family note: /,
      "",
    ) || "",
  };
}
const originals = Object.fromEntries(
  rows.map((row) => [row.dataset.key, originalFor(row)]),
);
function saveState() {
  localStorage.setItem(storageKey, JSON.stringify(corrections));
  document.getElementById("editCount").textContent =
    Object.keys(corrections).length + " saved passage" +
    (Object.keys(corrections).length === 1 ? "" : "s");
}
Object.entries(corrections).forEach(([key, edit]) => {
  const base = originals[key];
  if (
    base && edit.speaker === base.speaker &&
    String(edit.text || "").replaceAll("*", "") === base.text &&
    String(edit.note || "").trim() === base.note
  ) delete corrections[key];
});
function renderTranscript(target, value) {
  target.replaceChildren();
  String(value).split("*").forEach((part, index) => {
    if (index % 2) {
      const em = document.createElement("em");
      em.textContent = part;
      target.appendChild(em);
    } else target.appendChild(document.createTextNode(part));
  });
}
function applyCorrection(row) {
  const edit = corrections[row.dataset.key], base = originals[row.dataset.key];
  row.querySelector(".speaker").textContent = (edit?.speaker || base.speaker) +
    ":";
  renderTranscript(
    row.querySelector(".transcript-text"),
    edit?.text || base.text,
  );
  row.classList.toggle("corrected", !!edit);
  let note = row.querySelector(".correction-note");
  if (edit?.note) {
    if (!note) {
      note = document.createElement("span");
      note.className = "correction-note";
      row.querySelector("p").appendChild(note);
    }
    note.textContent = "Family note: " + edit.note;
  } else if (note) note.remove();
}
rows.forEach(applyCorrection);
saveState();
function closeEditor(editor) {
  editor.remove();
  if (!document.querySelector(".editor")) playbackStopAt = null;
}
function limitPlaybackTo(row) {
  playbackStopAt = +row.dataset.end;
  if (
    playerReady && typeof player.getCurrentTime === "function" &&
    player.getCurrentTime() >= playbackStopAt
  ) player.pauseVideo();
}
function openEditor(row) {
  let editor = row.querySelector(".editor");
  if (editor) {
    closeEditor(editor);
    return;
  }
  limitPlaybackTo(row);
  if (playerReady) player.pauseVideo();
  const key = row.dataset.key,
    base = originals[key],
    edit = corrections[key] || {};
  editor = document.createElement("div");
  editor.className = "editor";
  const speaker = document.createElement("select");
  speakerOptions.forEach((name) => {
    const option = document.createElement("option");
    option.value = option.textContent = name;
    speaker.appendChild(option);
  });
  speaker.value = edit.speaker || base.speaker;
  const text = document.createElement("textarea");
  text.className = "edit-text";
  text.value = edit.text || base.text;
  const note = document.createElement("textarea");
  note.className = "edit-note";
  note.placeholder =
    "Names, context, uncertainty, translation, or anything else to tell the editor";
  note.value = edit.note || "";
  const speakerLabel = document.createElement("label");
  speakerLabel.textContent = "Speaker";
  speakerLabel.appendChild(speaker);
  const textLabel = document.createElement("label");
  textLabel.textContent = "Corrected transcript";
  textLabel.appendChild(text);
  const noteLabel = document.createElement("label");
  noteLabel.textContent = "Family note";
  noteLabel.appendChild(note);
  const controls = document.createElement("div");
  controls.className = "editor-buttons";
  const close = document.createElement("button");
  close.type = "button";
  close.textContent = "Close";
  close.onclick = () => closeEditor(editor);
  const discard = document.createElement("button");
  discard.type = "button";
  discard.textContent = "Discard saved correction";
  discard.onclick = () => {
    delete corrections[key];
    saveState();
    applyCorrection(row);
    closeEditor(editor);
  };
  const saved = document.createElement("span");
  saved.className = "autosave";
  saved.textContent = "Changes autosave";
  controls.append(close, discard, saved);
  editor.append(speakerLabel, textLabel, noteLabel, controls);
  function update() {
    const next = {
      start: base.start,
      end: base.end,
      original_speaker: base.speaker,
      original_text: base.text,
      speaker: speaker.value,
      text: text.value,
      note: note.value,
      updated_at: new Date().toISOString(),
    };
    const unchanged = next.speaker === base.speaker &&
      next.text === base.text && !next.note.trim();
    if (unchanged) delete corrections[key];
    else corrections[key] = next;
    saveState();
    applyCorrection(row);
  }
  speaker.onchange = update;
  text.oninput = update;
  note.oninput = update;
  row.querySelector(".utterance-main").appendChild(editor);
}
document.querySelectorAll(".edit-toggle").forEach((button) =>
  button.onclick = () => openEditor(button.closest(".utterance"))
);
document.getElementById("exportEdits").onclick = () => {
  const payload = {
    format: "abe-tabak-family-corrections-v1",
    recording: config.export_recording,
    video_id: config.media_id,
    exported_at: new Date().toISOString(),
    corrections: Object.values(corrections).sort((a, b) => a.start - b.start),
  };
  const blob = new Blob([JSON.stringify(payload, null, 2) + "\n"], {
      type: "application/json",
    }),
    url = URL.createObjectURL(blob),
    a = document.createElement("a");
  a.href = url;
  a.download = config.export_filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
document.getElementById("importEdits").onchange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    const payload = JSON.parse(await file.text());
    if (
      payload.format !== "abe-tabak-family-corrections-v1" ||
      !Array.isArray(payload.corrections)
    ) throw new Error("Unrecognized correction file");
    if (
      (payload.video_id && payload.video_id !== config.media_id) ||
      (payload.recording && payload.recording !== config.export_recording)
    ) throw new Error("This correction file belongs to another recording");
    payload.corrections.forEach((edit) => {
      corrections[Number(edit.start).toFixed(3)] = edit;
    });
    saveState();
    rows.forEach(applyCorrection);
    alert("Imported " + payload.corrections.length + " corrections.");
  } catch (error) {
    alert("Could not import this file: " + error.message);
  }
  event.target.value = "";
};
window.onYouTubeIframeAPIReady = () => {
  player = new YT.Player("youtubePlayer", {
    events: {
      onReady: () => {
        playerReady = true;
        status.textContent = "Ready. Click a timestamp to play that passage.";
        if (pendingSeek !== null) {
          seek(pendingSeek);
          pendingSeek = null;
        }
      },
      onError: () => {
        status.textContent =
          "The embedded player could not load. Open the video on YouTube.";
      },
    },
  });
};
const api = document.createElement("script");
api.src = "https://www.youtube.com/iframe_api";
document.head.appendChild(api);
function seek(t) {
  t = Number(t);
  if (playerReady) {
    player.seekTo(t, true);
    player.playVideo();
  } else {
    pendingSeek = t;
    status.textContent = "Waiting for the player…";
  }
}
document.querySelectorAll("[data-seek]").forEach((x) =>
  x.onclick = (e) => {
    if (x.tagName === "A") {
      e.preventDefault();
      const chapter = document.querySelector(x.getAttribute("href"));
      if (chapter) {
        chapter.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
    const editorRow = document.querySelector(".editor")?.closest(".utterance");
    if (editorRow && x.closest(".utterance")) limitPlaybackTo(editorRow);
    else playbackStopAt = null;
    seek(x.dataset.seek);
  }
);
let activeRow = null;
function editingTranscript() {
  const focused = document.activeElement;
  return !!focused?.closest?.(".editor");
}
function followRow(row) {
  if (
    !document.getElementById("followPlayback").checked || editingTranscript() ||
    document.getElementById("transcript").hidden
  ) return;
  const box = row.getBoundingClientRect(),
    playerBox = document.querySelector(".player").getBoundingClientRect(),
    top = Math.min(
      window.innerHeight - 90,
      Math.max(16, playerBox.bottom + 16),
    ),
    bottom = Math.max(top + 70, window.innerHeight - 24);
  if (box.top < top || box.bottom > bottom) {
    window.scrollBy({ top: box.top - top, behavior: "smooth" });
  }
}
setInterval(() => {
  if (!playerReady || typeof player.getCurrentTime !== "function") return;
  const t = player.getCurrentTime();
  if (playbackStopAt !== null && t >= playbackStopAt) player.pauseVideo();
  const next = rows.find((r) =>
    !r.hidden && t >= +r.dataset.start && t < +r.dataset.end
  ) || null;
  if (next === activeRow) {
    return;
  }
  if (activeRow) {
    activeRow.classList.remove("active");
  }
  activeRow = next;
  if (activeRow) {
    activeRow.classList.add("active");
    if (
      typeof player.getPlayerState !== "function" ||
      player.getPlayerState() === YT.PlayerState.PLAYING
    ) {
      followRow(activeRow);
    }
  }
}, 100);
function filter() {
  const q = document.getElementById("search").value.toLowerCase(),
    review = document.getElementById("review").checked;
  let n = 0;
  rows.forEach((r) => {
    r.hidden = !(r.textContent.toLowerCase().includes(q) &&
      (!review || r.classList.contains("review")));
    if (!r.hidden) n++;
  });
  document.querySelectorAll(".chapter").forEach((c) =>
    c.hidden = ![...c.querySelectorAll(".utterance")].some((r) => !r.hidden)
  );
  document.getElementById("count").textContent = n + " passages";
}
document.getElementById("search").oninput = filter;
document.getElementById("review").onchange = filter;
filter();
document.querySelectorAll("[data-panel]").forEach((b) =>
  b.onclick = () => {
    document.querySelectorAll("[data-panel]").forEach((x) =>
      x.classList.toggle("selected", x === b)
    );
    document.getElementById("transcript").hidden =
      b.dataset.panel !== "transcript";
    document.getElementById("notes").hidden = b.dataset.panel !== "notes";
  }
);
