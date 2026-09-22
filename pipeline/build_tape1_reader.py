import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "work" / "tapes" / "pilot-tape1"
speaker_transcript = PILOT / "transcript-speakers.json"
data = json.loads((speaker_transcript if speaker_transcript.exists() else PILOT / "transcript.json").read_text())
rows = data["segments"]

chapters = [
    (0, "Relatives, marriage, and World War I"),
    (266, "Abe’s earliest memories"),
    (420, "Cheder and an older brother’s wedding"),
    (700, "Evacuation from Krasnobród"),
    (925, "Shelter and trading around Zamość"),
    (1170, "Return to Krasnobród and wartime money"),
    (1390, "Hunger, epidemic, and the Russian Jewish doctor"),
    (1620, "His mother’s illness and death"),
    (1810, "Polish conscription and family ages"),
    (2320, "Learning the shoemaking trade"),
    (2580, "Trading food between Krasnobród and Tomaszów"),
    (2820, "Shoemaking, customers, and illness"),
    (3300, "Summer visitors and teenage courtship"),
]

annotations = [
    ("Names and relationships", "Several names in the opening are still phonetic machine readings. They remain unresolved until checked against the audio and family records."),
    ("Cheder", "At about 00:05:00, the recognizer writes “Haida.” Abe is describing cheder, the traditional Jewish elementary school where boys began religious study."),
    ("Nadn", "At about 00:08:00, Abe explains the Yiddish word nadn: the dowry or marriage portion associated with a match."),
    ("Place names", "Machine variants such as Krasenbord, Samish, Tomshof, and Tomaschow likely refer to Krasnobród, Zamość, and Tomaszów Lubelski. The draft preserves the spoken evidence pending close listening."),
    ("The doctor", "At about 00:24:00, Abe describes a Russian Jewish physician who was an Austrian prisoner of war and visited homes during an epidemic."),
    ("Language", "The conversation is mostly English with Yiddish, Polish, and Yinglish words. Unfamiliar words are retained phonetically rather than replaced with guesses."),
]

def ts(value):
    value = int(value)
    return f"{value // 3600:02}:{value // 60 % 60:02}:{value % 60:02}"

def chapter_for(value):
    return max(i for i, (start, _) in enumerate(chapters) if start <= value)

nav = "".join(
    f'<a href="#chapter-{i}" data-seek="{start}"><time>{ts(start)}</time>{html.escape(title)}</a>'
    for i, (start, title) in enumerate(chapters)
)

article = []
current = -1
for row in rows:
    chapter = chapter_for(row["start"])
    if chapter != current:
        if current >= 0:
            article.append("</section>")
        current = chapter
        article.append(
            f'<section class="chapter" id="chapter-{chapter}"><h2><small>{ts(chapters[chapter][0])}</small>{html.escape(chapters[chapter][1])}</h2>'
        )
    review = " review" if row["needs_review"] else ""
    badge = '<span class="badge">Check audio</span>' if row["needs_review"] else ""
    speaker_name = row.get("speaker") or "Unclear speaker"
    speaker = f'<strong class="speaker">{html.escape(speaker_name)}:</strong> '
    key = f'{row["start"]:.3f}'
    article.append(
        f'<div class="utterance{review}" data-key="{key}" data-start="{row["start"]}" data-end="{row["end"]}">'
        f'<button class="stamp" data-seek="{row["start"]}">{ts(row["start"])}</button>'
        f'<div class="utterance-main"><p>{badge}{speaker}<span class="transcript-text">{html.escape(row["text"])}</span></p>'
        f'<button class="edit-toggle" type="button">Correct or annotate</button></div></div>'
    )
article.append("</section>")

notes = "".join(f"<h3>{html.escape(title)}</h3><p>{html.escape(text)}</p>" for title, text in annotations)

page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Abe Tabak tapes · Tape 1 pilot</title>
<style>
:root{{--paper:#f6f1e7;--ink:#252b26;--muted:#657069;--accent:#8b3e2f;--rule:#d4cdbf;--active:#e4eadb}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,sans-serif}}
header{{padding:48px max(24px,calc((100vw - 1180px)/2));border-bottom:1px solid var(--rule)}}
.eyebrow{{text-transform:uppercase;letter-spacing:.13em;color:var(--accent);font-size:12px;font-weight:700}}
h1{{font:52px/1.05 Georgia,serif;margin:12px 0}}header p{{font:20px/1.5 Georgia,serif;max-width:800px}}
.layout{{display:grid;grid-template-columns:245px minmax(0,760px);gap:48px;max-width:1180px;margin:auto;padding:30px 24px 80px}}
aside{{position:sticky;top:18px;align-self:start;max-height:90vh;overflow:auto}}aside h2{{font-size:12px;text-transform:uppercase;letter-spacing:.1em}}
aside a{{display:grid;grid-template-columns:62px 1fr;gap:8px;padding:7px 0;color:inherit;text-decoration:none;font-size:12px}}aside time{{color:var(--muted);font-family:monospace}}
.notice{{border:1px solid var(--rule);padding:14px 16px;font-size:13px;line-height:1.5}}
.player{{position:sticky;top:8px;z-index:10;background:var(--paper);border:1px solid var(--rule);padding:12px;margin:20px 0;box-shadow:0 5px 18px #26342c18}}
#youtubePlayer{{display:block;width:100%;aspect-ratio:16/9;border:0;background:#111}}.player p{{margin:8px 0 0;color:var(--muted);font-size:12px}}.toolbar{{display:flex;flex-wrap:wrap;gap:12px;margin:18px 0}}input[type=search]{{flex:1;min-width:220px;padding:10px;border:1px solid var(--rule);background:#fff}}
.review-tools{{border:1px solid var(--rule);background:#fffaf1;padding:14px 16px;margin:18px 0;font-size:13px;line-height:1.5}}.review-actions{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}}.review-actions button,.import-label{{border:1px solid var(--rule);border-radius:4px;background:white;padding:8px 11px;font:600 12px system-ui;cursor:pointer}}.import-label input{{display:none}}#editCount{{color:var(--muted);margin-left:auto;align-self:center}}
.chapter{{scroll-margin-top:120px}}.chapter h2{{font:28px/1.25 Georgia,serif;border-top:1px solid var(--rule);padding-top:24px;margin-top:40px}}.chapter h2 small{{display:block;font:12px monospace;color:var(--muted)}}
.utterance{{display:grid;grid-template-columns:72px 1fr;gap:14px;padding:6px;border-radius:4px}}.utterance.active{{background:var(--active)}}.utterance.corrected{{box-shadow:inset 3px 0 var(--accent);background:#fff8ec}}.utterance p{{font:17px/1.6 Georgia,serif;margin:0}}.utterance-main{{min-width:0}}
.stamp{{border:0;background:none;color:var(--muted);font:11px monospace;cursor:pointer;align-self:start;padding-top:6px}}.speaker{{font-family:system-ui,sans-serif;font-size:13px;color:var(--accent)}}.badge{{display:block;color:#8a5a21;font:700 10px system-ui;text-transform:uppercase}}
.edit-toggle{{border:0;background:none;color:var(--muted);padding:3px 0;font:11px system-ui;text-decoration:underline}}.correction-note{{display:block;margin-top:5px;color:var(--muted);font:12px/1.45 system-ui;border-left:2px solid var(--accent);padding-left:8px}}.editor{{margin-top:8px;border:1px solid var(--rule);background:white;padding:12px;display:grid;gap:9px}}.editor label{{display:grid;gap:4px;font:600 11px system-ui;color:var(--muted)}}.editor select,.editor textarea{{width:100%;border:1px solid var(--rule);border-radius:3px;padding:8px;font:14px/1.4 system-ui;color:var(--ink);background:white}}.editor textarea.edit-text{{min-height:88px}}.editor textarea.edit-note{{min-height:60px}}.editor-buttons{{display:flex;gap:8px}}.editor-buttons button{{border:1px solid var(--rule);border-radius:3px;background:white;padding:7px 10px;font:12px system-ui}}.autosave{{color:var(--muted);font:11px system-ui}}
.tabs{{display:flex;gap:8px;margin:24px 0}}.tabs button{{padding:9px 14px;border:1px solid var(--rule);background:transparent}}.tabs button.selected{{background:var(--ink);color:#fff}}
.notes h3{{margin-top:28px}}.notes p{{line-height:1.6}}[hidden]{{display:none!important}}
@media(max-width:800px){{h1{{font-size:39px}}.layout{{display:block}}aside{{position:static;max-height:220px;margin-bottom:24px}}.utterance{{grid-template-columns:63px 1fr}}}}
</style></head><body>
<header><div class="eyebrow">Family oral history · pilot transcript</div><h1>Abe Tabak tapes</h1><p>Tape 1 · Bella (Rita), Nina, Len, and Abraham “Abe” Tabak · 1:03:36</p></header>
<div class="layout"><aside><h2>In this recording</h2>{nav}</aside><main>
<div class="notice"><strong>Working transcript.</strong> Automatic speaker detection found one stable Abe voice and one interviewer voice identified by the family as Bella. Mixed passages are labeled explicitly. Close-listening corrections, Yiddish transcription, and translation remain under editorial review.</div>
<div class="player"><iframe id="youtubePlayer" title="The Abe Tabak Tapes — Tape 1" src="https://www.youtube.com/embed/fJDnT9XBD58?enablejsapi=1&amp;playsinline=1&amp;rel=0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><p id="playerStatus">Loading YouTube player…</p></div>
<div class="tabs"><button class="selected" data-panel="transcript">Transcript</button><button data-panel="notes">Annotations</button></div>
<section id="transcript"><div class="review-tools"><strong>Family review workspace</strong><br>Use “Correct or annotate” beside any passage. Changes save only in this browser. Export the correction file when you are ready to share it; importing a previous export merges it into this browser’s saved work.<div class="review-actions"><button id="exportEdits" type="button">Export corrections (.json)</button><label class="import-label">Import corrections<input id="importEdits" type="file" accept="application/json,.json"></label><span id="editCount"></span></div></div><div class="toolbar"><input id="search" type="search" placeholder="Search the transcript…"><label><input id="review" type="checkbox"> Check audio only</label><label><input id="followPlayback" type="checkbox" checked> Follow playback</label></div><div id="count"></div>{''.join(article)}</section>
<section id="notes" class="notes" hidden>{notes}</section>
</main></div><script>
const rows=[...document.querySelectorAll('.utterance')],status=document.getElementById('playerStatus'),storageKey='abe-tabak-tape1-corrections-v1',speakerOptions=['Abe','Bella','Nina','Len','Dan','Multiple speakers','Unclear speaker'];let player=null,playerReady=false,pendingSeek=null,corrections={{}};
try{{corrections=JSON.parse(localStorage.getItem(storageKey)||'{{}}');}}catch(e){{corrections={{}};}}
function originalFor(row){{return{{start:+row.dataset.start,end:+row.dataset.end,text:row.querySelector('.transcript-text').textContent,speaker:row.querySelector('.speaker').textContent.replace(/:$/,'')}};}}
const originals=Object.fromEntries(rows.map(row=>[row.dataset.key,originalFor(row)]));
function saveState(){{localStorage.setItem(storageKey,JSON.stringify(corrections));document.getElementById('editCount').textContent=Object.keys(corrections).length+' saved passage'+(Object.keys(corrections).length===1?'':'s');}}
function applyCorrection(row){{const edit=corrections[row.dataset.key],base=originals[row.dataset.key];row.querySelector('.speaker').textContent=(edit?.speaker||base.speaker)+':';row.querySelector('.transcript-text').textContent=edit?.text||base.text;row.classList.toggle('corrected',!!edit);let note=row.querySelector('.correction-note');if(edit?.note){{if(!note){{note=document.createElement('span');note.className='correction-note';row.querySelector('p').appendChild(note);}}note.textContent='Family note: '+edit.note;}}else if(note)note.remove();}}
rows.forEach(applyCorrection);saveState();
function openEditor(row){{let editor=row.querySelector('.editor');if(editor){{editor.remove();return;}}const key=row.dataset.key,base=originals[key],edit=corrections[key]||{{}};editor=document.createElement('div');editor.className='editor';const speaker=document.createElement('select');speakerOptions.forEach(name=>{{const option=document.createElement('option');option.value=option.textContent=name;speaker.appendChild(option);}});speaker.value=edit.speaker||base.speaker;const text=document.createElement('textarea');text.className='edit-text';text.value=edit.text||base.text;const note=document.createElement('textarea');note.className='edit-note';note.placeholder='Names, context, uncertainty, translation, or anything else to tell the editor';note.value=edit.note||'';const speakerLabel=document.createElement('label');speakerLabel.textContent='Speaker';speakerLabel.appendChild(speaker);const textLabel=document.createElement('label');textLabel.textContent='Corrected transcript';textLabel.appendChild(text);const noteLabel=document.createElement('label');noteLabel.textContent='Family note';noteLabel.appendChild(note);const controls=document.createElement('div');controls.className='editor-buttons';const close=document.createElement('button');close.type='button';close.textContent='Close';close.onclick=()=>editor.remove();const discard=document.createElement('button');discard.type='button';discard.textContent='Discard saved correction';discard.onclick=()=>{{delete corrections[key];saveState();applyCorrection(row);editor.remove();}};const saved=document.createElement('span');saved.className='autosave';saved.textContent='Changes autosave';controls.append(close,discard,saved);editor.append(speakerLabel,textLabel,noteLabel,controls);function update(){{const next={{start:base.start,end:base.end,original_speaker:base.speaker,original_text:base.text,speaker:speaker.value,text:text.value,note:note.value,updated_at:new Date().toISOString()}};const unchanged=next.speaker===base.speaker&&next.text===base.text&&!next.note.trim();if(unchanged)delete corrections[key];else corrections[key]=next;saveState();applyCorrection(row);}}speaker.onchange=update;text.oninput=update;note.oninput=update;row.querySelector('.utterance-main').appendChild(editor);}}
document.querySelectorAll('.edit-toggle').forEach(button=>button.onclick=()=>openEditor(button.closest('.utterance')));
document.getElementById('exportEdits').onclick=()=>{{const payload={{format:'abe-tabak-family-corrections-v1',recording:'Tape 1',video_id:'fJDnT9XBD58',exported_at:new Date().toISOString(),corrections:Object.values(corrections).sort((a,b)=>a.start-b.start)}};const blob=new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='Abe_Tabak_Tape_1_family_corrections.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}};
document.getElementById('importEdits').onchange=async event=>{{const file=event.target.files[0];if(!file)return;try{{const payload=JSON.parse(await file.text());if(payload.format!=='abe-tabak-family-corrections-v1'||!Array.isArray(payload.corrections))throw new Error('Unrecognized correction file');payload.corrections.forEach(edit=>{{corrections[Number(edit.start).toFixed(3)]=edit;}});saveState();rows.forEach(applyCorrection);alert('Imported '+payload.corrections.length+' corrections.');}}catch(error){{alert('Could not import this file: '+error.message);}}event.target.value='';}};
window.onYouTubeIframeAPIReady=()=>{{player=new YT.Player('youtubePlayer',{{events:{{onReady:()=>{{playerReady=true;status.textContent='Ready. Click a timestamp to play that passage.';if(pendingSeek!==null){{seek(pendingSeek);pendingSeek=null;}}}},onError:()=>{{status.textContent='The embedded player could not load. Open the video on YouTube.';}}}}}});}};
const api=document.createElement('script');api.src='https://www.youtube.com/iframe_api';document.head.appendChild(api);
function seek(t){{t=Number(t);if(playerReady){{player.seekTo(t,true);player.playVideo();}}else{{pendingSeek=t;status.textContent='Waiting for the player…';}}}}
document.querySelectorAll('[data-seek]').forEach(x=>x.onclick=e=>{{if(x.tagName==='A'){{e.preventDefault();const chapter=document.querySelector(x.getAttribute('href'));if(chapter)chapter.scrollIntoView({{behavior:'smooth',block:'start'}});}}seek(x.dataset.seek);}});
let activeRow=null;
function editingTranscript(){{const focused=document.activeElement;return !!focused?.closest?.('.editor');}}
function followRow(row){{if(!document.getElementById('followPlayback').checked||editingTranscript()||document.getElementById('transcript').hidden)return;const box=row.getBoundingClientRect(),top=Math.max(120,window.innerHeight*.22),bottom=window.innerHeight*.78;if(box.top<top||box.bottom>bottom)row.scrollIntoView({{behavior:'smooth',block:'center'}});}}
setInterval(()=>{{if(!playerReady||typeof player.getCurrentTime!=='function')return;const t=player.getCurrentTime(),next=rows.find(r=>!r.hidden&&t>=+r.dataset.start&&t<+r.dataset.end)||null;if(next===activeRow)return;if(activeRow)activeRow.classList.remove('active');activeRow=next;if(activeRow){{activeRow.classList.add('active');if(typeof player.getPlayerState!=='function'||player.getPlayerState()===YT.PlayerState.PLAYING)followRow(activeRow);}}}},300);
function filter(){{const q=document.getElementById('search').value.toLowerCase(),review=document.getElementById('review').checked;let n=0;rows.forEach(r=>{{r.hidden=!(r.textContent.toLowerCase().includes(q)&&(!review||r.classList.contains('review')));if(!r.hidden)n++;}});document.querySelectorAll('.chapter').forEach(c=>c.hidden=![...c.querySelectorAll('.utterance')].some(r=>!r.hidden));document.getElementById('count').textContent=n+' passages';}}
document.getElementById('search').oninput=filter;document.getElementById('review').onchange=filter;filter();
document.querySelectorAll('[data-panel]').forEach(b=>b.onclick=()=>{{document.querySelectorAll('[data-panel]').forEach(x=>x.classList.toggle('selected',x===b));document.getElementById('transcript').hidden=b.dataset.panel!=='transcript';document.getElementById('notes').hidden=b.dataset.panel!=='notes';}});
</script></body></html>'''
(PILOT / "index.html").write_text(page)
print(f"Wrote {PILOT / 'index.html'}")
