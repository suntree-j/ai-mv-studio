import React from "react";
import { AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame, interpolate, delayRender, continueRender } from "remotion";

export type PackShot = { file: string; start: number; end: number; motion: string; lum?: number };
export type PackLyric = { start: number; end: number; text: string };
export type PackProps = { song: string; original_artist?: string; fps: number; total_frames: number; shots: PackShot[]; lyrics?: PackLyric[]; audio_start_seconds?: number };

const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));

const FONT = "MaShanZheng";
let fontPromise: Promise<void> | null = null;
const loadFont = () => {
  if (fontPromise) return fontPromise;
  fontPromise = new Promise<void>((resolve) => {
    try {
      const f = new (window as any).FontFace(FONT, `url(${staticFile("fonts/MaShanZheng-Regular.ttf")})`);
      f.load().then(() => {
        (document as any).fonts.add(f);
        resolve();
      }).catch(() => resolve());
    } catch {
      resolve();
    }
  });
  return fontPromise;
};

const useFont = () => {
  const [handle] = React.useState(() => delayRender("font"));
  React.useEffect(() => {
    loadFont().then(() => continueRender(handle));
  }, [handle]);
};

const Shot: React.FC<{ s: PackShot }> = ({ s }) => {
  const frame = useCurrentFrame();
  const dur = Math.max(1, s.end - s.start);
  const t = clamp(frame / dur);
  let scale = 1.04, tx = 0, ty = 0;
  const m = (s.motion || "").toLowerCase();
  if (m.includes("pull") || m.includes("out")) scale = 1.12 - 0.08 * t;
  else if (m.includes("pan_left") || m.includes("left")) { scale = 1.10; tx = -30 + 60 * t; }
  else if (m.includes("pan_right") || m.includes("right")) { scale = 1.10; tx = 30 - 60 * t; }
  else if (m.includes("up") || m.includes("rise")) { scale = 1.10; ty = 20 - 40 * t; }
  else scale = 1.02 + 0.09 * t;
  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [dur - 12, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: Math.min(fadeIn, fadeOut) }}>
      <Img src={staticFile(s.file)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale}) translate(${tx}px, ${ty}px)` }} />
    </AbsoluteFill>
  );
};

const IntroInfo: React.FC<{ artist?: string; song?: string }> = ({ artist, song }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12, 90, 108], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const title = song ? `《${song}》` : "";
  const line = `原唱：${artist || "—"}    ·    AI 合成：双笙音色    ·    个人自用 · 非商用`;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 38, pointerEvents: "none" }}>
      <div style={{ opacity, textAlign: "center", fontFamily: '"MaShanZheng","STKaiti",serif', color: "#f2ead6", textShadow: "0 2px 12px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.85)" }}>
        <div style={{ fontSize: 52, letterSpacing: 6, marginBottom: 8 }}>{title}</div>
        <div style={{ fontSize: 30, letterSpacing: 3, color: "#e8dfc6" }}>{line}</div>
      </div>
    </AbsoluteFill>
  );
};

const hash = (s: string) => { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 9973; return h; };

const LyricLine: React.FC<{ l: PackLyric; idx: number; shots: PackShot[] }> = ({ l, idx, shots }) => {
  useFont();
  const frame = useCurrentFrame();
  const dur = Math.max(1, l.end - l.start);
  const fadeIn = interpolate(frame, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [dur - 10, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const h = hash(l.text + idx);
  const layout = h % 5;
  const vertical = layout === 0 || layout === 2 || layout === 4;
  const text = l.text;
  const len = text.length;

  // 按当前时间所处镜头判断背景亮度，自动选高对比色
  const globalFrame = l.start + frame;
  const shot = shots.find((s) => globalFrame >= s.start && globalFrame < s.end) || shots[0];
  const lum = shot?.lum ?? 0.5;
  const darkBg = lum < 0.58;
  const color = darkBg ? "#f8f2e3" : "#1e1915";
  const stroke = darkBg ? "1.2px rgba(0,0,0,0.55)" : "1.2px rgba(255,255,255,0.55)";
  const shadow = darkBg
    ? "0 2px 12px rgba(0,0,0,0.85), 0 0 3px rgba(0,0,0,0.8)"
    : "0 2px 12px rgba(255,255,255,0.65), 0 0 3px rgba(255,255,255,0.6)";

  // 按自然断句（标点/空格）拆短语，再按短语打包成行/列
  const phrases = text.split(/(?<=[，。、；：！？,.\s~～…—])/).filter((p) => p.trim().length > 0);
  const packToLines = (units: string[], maxChars: number): string[] => {
    const out: string[] = [];
    let cur = "";
    for (const u of units) {
      if (u.length > maxChars) {
        if (cur) { out.push(cur); cur = ""; }
        for (let i = 0; i < u.length; i += maxChars) out.push(u.slice(i, i + maxChars));
        continue;
      }
      if ((cur + u).length > maxChars) { if (cur) out.push(cur); cur = u; }
      else cur += u;
    }
    if (cur) out.push(cur);
    return out;
  };

  // 字号根据最长短句自适应：保证一句完整放进一列（竖）或一行（横）
  const longest = Math.max(...phrases.map((p) => p.length), 1);
  const maxByHeight = Math.floor(760 / (longest * 1.15));
  const fontSize = Math.min(len <= 10 ? 70 : len <= 16 ? 62 : len <= 24 ? 54 : len <= 36 ? 46 : 40, Math.max(34, maxByHeight));
  const maxColChars = Math.max(6, Math.floor(760 / (fontSize * 1.15)));
  const maxRowChars = Math.max(8, Math.floor(1450 / (fontSize * 1.1)));
  const cols = packToLines(phrases, maxColChars);
  const rows = packToLines(phrases, maxRowChars);

  const posStyle: React.CSSProperties = {};
  if (layout === 0) { posStyle.left = "6%"; posStyle.top = "10%"; }
  else if (layout === 1) { posStyle.right = "7%"; posStyle.top = "50%"; }
  else if (layout === 2) { posStyle.right = "6%"; posStyle.top = "10%"; }
  else if (layout === 3) { posStyle.left = "7%"; posStyle.bottom = "14%"; }
  else { posStyle.left = "10%"; posStyle.bottom = "12%"; }

  const rot = (h % 5) - 2;
  const base: React.CSSProperties = {
    opacity: Math.min(fadeIn, fadeOut) * 0.94,
    transform: `rotate(${rot}deg)`,
    color,
    fontFamily: `"${FONT}","STKaiti","KaiTi",serif`,
    fontSize,
    lineHeight: 1.15,
    letterSpacing: 4,
    textShadow: shadow,
    WebkitTextStroke: stroke,
    fontWeight: 500,
  };

  let content: React.ReactNode;
  if (vertical) {
    content = (
      <div style={{ display: "flex", flexDirection: "row", gap: 10 }}>
        {cols.map((c, i) => (
          <div key={i} style={{ writingMode: "vertical-rl", maxHeight: "72vh", whiteSpace: "pre-wrap" }}>{c}</div>
        ))}
      </div>
    );
  } else {
    content = (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 6 }}>
        {rows.map((r, i) => (
          <div key={i} style={{ writingMode: "horizontal-tb", whiteSpace: "pre-wrap", textAlign: "left" }}>{r}</div>
        ))}
      </div>
    );
  }

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", ...posStyle, ...base }}>{content}</div>
    </AbsoluteFill>
  );
};

export const PackMV: React.FC<PackProps> = ({ song, shots, total_frames, lyrics, original_artist }) => {
  useFont();
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0f0d" }}>
      {shots.map((s, i) => (
        <Sequence key={i} from={s.start} durationInFrames={Math.max(1, s.end - s.start)}>
          <Shot s={s} />
        </Sequence>
      ))}
      <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 48%, rgba(0,0,0,0.32) 100%)", pointerEvents: "none" }} />
      <AbsoluteFill style={{ boxShadow: "inset 0 0 130px 45px rgba(0,0,0,0.5)", pointerEvents: "none" }} />
      <IntroInfo artist={original_artist} song={song} />
      {(lyrics || []).map((l, i) => (
        <Sequence key={"ly" + i} from={l.start} durationInFrames={Math.max(1, l.end - l.start)}>
          <LyricLine l={l} idx={i} shots={shots} />
        </Sequence>
      ))}
      <Sequence durationInFrames={Math.max(1, total_frames)} name="total">{null}</Sequence>
    </AbsoluteFill>
  );
};
