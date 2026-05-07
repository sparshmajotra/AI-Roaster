"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  EyeOff,
  Flame,
  Globe2,
  ImageIcon,
  LoaderCircle,
  Lock,
  Send,
  ShieldCheck,
  Sparkles,
  Type,
  Upload,
} from "lucide-react";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { createRoastPost, getDemoToken, type RoastPostResponse } from "@/lib/api";
import { aiPreview, categories, feedPosts, type RoastCategory, roastStyles, type RoastStyle } from "@/lib/roastly-data";

type ComposeMode = "text" | "image";
type Visibility = "public" | "private" | "anonymous";

type RoastResult = {
  roast: string;
  score: string;
  aura: string;
  tags: string[];
  tips: string[];
  status?: string;
};

const visibilityOptions: Array<{ value: Visibility; label: string; icon: typeof Globe2 }> = [
  { value: "public", label: "Public", icon: Globe2 },
  { value: "private", label: "Private", icon: Lock },
  { value: "anonymous", label: "Anon", icon: EyeOff },
];

export function RoastlyApp() {
  const [mode, setMode] = useState<ComposeMode>("text");
  const [category, setCategory] = useState<RoastCategory>("Roast My Bio");
  const [style, setStyle] = useState<RoastStyle>("Brutal Roast");
  const [visibility, setVisibility] = useState<Visibility>("public");
  const [textContent, setTextContent] = useState(
    "My dating profile says I love coffee, late-night drives, and pretending I have a five-year plan.",
  );
  const [selectedFile, setSelectedFile] = useState<File | undefined>();
  const [isGenerating, setIsGenerating] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [result, setResult] = useState<RoastResult>({
    roast: aiPreview.roast,
    score: aiPreview.score.toString(),
    aura: aiPreview.aura,
    tags: aiPreview.tags,
    tips: aiPreview.tips,
  });

  const selectedCategory = useMemo(
    () => categories.find((item) => item.name === category) ?? categories[0],
    [category],
  );
  const CategoryIcon = selectedCategory.icon;

  const handleGenerate = async () => {
    setIsGenerating(true);
    setSubmitError("");

    try {
      let token = window.localStorage.getItem("roastly_demo_access");
      if (!token) {
        const demo = await getDemoToken();
        token = demo.access;
        window.localStorage.setItem("roastly_demo_access", token);
      }

      const response = await createRoastPost(
        {
          category,
          roast_style: style,
          visibility,
          text_content: textContent,
          media: mode === "image" ? selectedFile : undefined,
        },
        token,
      );

      setResult(mapRoastResponse(response));
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Could not create roast.");
      setResult({
        roast: [
          "Backend did not answer, so Roastly stayed in preview mode.",
          "The UI is awake, but the API needs its coffee.",
          "Start the backend on port 8000 and press Roast me again.",
          "Until then, this roast is just doing unpaid rehearsal.",
          "Even the loading spinner looked disappointed.",
        ].join("\n"),
        score: "7.4",
        aura: "Local Setup Drama",
        tags: ["api check", "local dev", "try again"],
        tips: ["Run start-roastly.bat", "Open http://127.0.0.1:3000 after both servers are ready"],
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <main className="min-h-screen px-4 py-5 text-[#f7f7f4] sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-5 flex items-center justify-between rounded-lg border border-white/10 bg-[#111116]/85 p-3 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="grid size-11 place-items-center rounded-lg bg-[#f7f7f4] text-[#08080b]">
              <Flame className="size-6 fill-[#ff5b5a] text-[#ff5b5a]" />
            </div>
            <div>
              <p className="text-xl font-black">Roastly</p>
              <p className="text-xs font-semibold text-[#a7a7b0]">AI roast generator</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-lg border border-[#8fff7a]/30 bg-[#8fff7a]/10 px-3 py-2 text-sm font-bold text-[#8fff7a] sm:flex">
            <ShieldCheck className="size-4" />
            Safe mode on
          </div>
        </header>

        <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_400px]">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-white/10 bg-[#111116]/90 p-4 shadow-2xl shadow-black/30 sm:p-5"
          >
            <div className="mb-5">
              <p className="mb-2 flex items-center gap-2 text-sm font-bold text-[#8fff7a]">
                <Sparkles className="size-4" />
                Create roast
              </p>
              <h1 className="text-3xl font-black leading-tight sm:text-5xl">
                Paste text, pick a style, get judged.
              </h1>
            </div>

            <div className="mb-4 grid grid-cols-2 rounded-lg border border-white/10 bg-[#08080b] p-1">
              <ModeButton active={mode === "text"} icon={Type} label="Text" onClick={() => setMode("text")} />
              <ModeButton active={mode === "image"} icon={ImageIcon} label="Image" onClick={() => setMode("image")} />
            </div>

            <AnimatePresence mode="wait">
              {mode === "text" ? (
                <motion.textarea
                  key="text"
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 8 }}
                  value={textContent}
                  onChange={(event) => setTextContent(event.target.value)}
                  className="focus-ring min-h-44 w-full resize-none rounded-lg border border-white/10 bg-[#08080b] p-4 text-base leading-7 text-white placeholder:text-[#777782]"
                  placeholder="Paste a bio, outfit description, dating profile, resume summary, or setup note."
                />
              ) : (
                <motion.label
                  key="image"
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 8 }}
                  className="grid min-h-44 cursor-pointer place-items-center rounded-lg border border-dashed border-white/20 bg-[#08080b] p-5 text-center"
                >
                  <input
                    type="file"
                    accept="image/*"
                    className="sr-only"
                    onChange={(event) => setSelectedFile(event.target.files?.[0])}
                  />
                  <div className="space-y-3">
                    <Upload className="mx-auto size-9 text-[#8fff7a]" />
                    <div>
                      <p className="font-black">{selectedFile ? selectedFile.name : "Choose image"}</p>
                      <p className="mt-1 text-sm text-[#a7a7b0]">Add text below for better roasts.</p>
                    </div>
                  </div>
                </motion.label>
              )}
            </AnimatePresence>

            {mode === "image" && (
              <textarea
                value={textContent}
                onChange={(event) => setTextContent(event.target.value)}
                className="focus-ring mt-3 min-h-24 w-full resize-none rounded-lg border border-white/10 bg-[#08080b] p-3 text-sm leading-6 text-white placeholder:text-[#777782]"
                placeholder="Optional image caption."
              />
            )}

            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <SelectField
                icon={<CategoryIcon className="size-4 text-[#8fff7a]" />}
                label="Category"
                value={category}
                onChange={(value) => setCategory(value as RoastCategory)}
                options={categories.map((item) => item.name)}
              />
              <SelectField
                icon={<Sparkles className="size-4 text-[#2dd4bf]" />}
                label="Style"
                value={style}
                onChange={(value) => setStyle(value as RoastStyle)}
                options={roastStyles}
              />
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]">
              <div className="grid grid-cols-3 rounded-lg border border-white/10 bg-[#08080b] p-1">
                {visibilityOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setVisibility(option.value)}
                    className={`focus-ring flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold transition ${
                      visibility === option.value ? "bg-white text-[#08080b]" : "text-[#c9c9d1] hover:bg-white/[0.08]"
                    }`}
                  >
                    <option.icon className="size-4" />
                    {option.label}
                  </button>
                ))}
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="focus-ring flex h-12 min-w-40 items-center justify-center gap-2 rounded-lg bg-[#8fff7a] px-5 text-sm font-black text-[#08080b] transition hover:bg-[#b5ff8f] disabled:cursor-wait disabled:opacity-70"
              >
                {isGenerating ? <LoaderCircle className="size-5 animate-spin" /> : <Send className="size-5" />}
                {isGenerating ? "Roasting" : "Roast me"}
              </button>
            </div>
          </motion.div>

          <motion.aside
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="rounded-lg border border-white/10 bg-[#111116]/90 p-4 shadow-2xl shadow-black/30 sm:p-5"
          >
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-bold text-[#a7a7b0]">Result</p>
                <p className="text-2xl font-black">{result.aura}</p>
              </div>
              <div className="grid size-20 place-items-center rounded-lg bg-[#ff5b5a] text-[#08080b]">
                <div className="text-center">
                  <p className="text-3xl font-black">{result.score}</p>
                  <p className="text-xs font-black">/10</p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-white/10 bg-[#08080b] p-4">
              <div className="space-y-2 text-lg font-bold leading-8">
                {result.roast.split("\n").filter(Boolean).map((line) => (
                  <p key={line}>{line}</p>
                ))}
              </div>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {result.tags.map((tag) => (
                <span key={tag} className="rounded-md border border-white/10 bg-white/[0.06] px-2.5 py-1 text-xs font-bold">
                  #{tag}
                </span>
              ))}
            </div>

            <div className="mt-4 space-y-2">
              {result.tips.map((tip) => (
                <div key={tip} className="flex gap-2 text-sm leading-6 text-[#d8d8dd]">
                  <CheckCircle2 className="mt-1 size-4 shrink-0 text-[#8fff7a]" />
                  <span>{tip}</span>
                </div>
              ))}
            </div>

            {submitError && (
              <p className="mt-4 flex gap-2 rounded-lg border border-[#ff5b5a]/40 bg-[#ff5b5a]/10 p-3 text-sm font-semibold text-[#ffb4ad]">
                <AlertTriangle className="mt-0.5 size-4 shrink-0" />
                {submitError}
              </p>
            )}
          </motion.aside>
        </section>

        <section className="mt-4 grid gap-3 md:grid-cols-3">
          {feedPosts.map((post) => (
            <article key={post.id} className="rounded-lg border border-white/10 bg-[#111116]/75 p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <p className="font-black">{post.author}</p>
                  <p className="text-sm text-[#a7a7b0]">{post.category}</p>
                </div>
                <span className="rounded-md bg-[#8fff7a] px-2 py-1 text-sm font-black text-[#08080b]">
                  {post.score}
                </span>
              </div>
              <p className="text-sm leading-6 text-[#d8d8dd]">{post.roast}</p>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

function ModeButton({
  active,
  icon: Icon,
  label,
  onClick,
}: {
  active: boolean;
  icon: typeof Type;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`focus-ring flex h-11 items-center justify-center gap-2 rounded-md text-sm font-black transition ${
        active ? "bg-white text-[#08080b]" : "text-[#c9c9d1] hover:bg-white/[0.08]"
      }`}
    >
      <Icon className="size-4" />
      {label}
    </button>
  );
}

function SelectField({
  icon,
  label,
  value,
  onChange,
  options,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <label>
      <span className="mb-2 block text-xs font-black text-[#a7a7b0]">{label}</span>
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2">{icon}</span>
        <select
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="focus-ring h-12 w-full appearance-none rounded-lg border border-white/10 bg-[#08080b] pl-10 pr-9 text-sm font-bold text-white"
        >
          {options.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-[#a7a7b0]" />
      </div>
    </label>
  );
}

function mapRoastResponse(response: RoastPostResponse): RoastResult {
  return {
    roast: response.ai_roast || "Roast queued.\nRefresh in a moment.\nThe backend accepted it.\nThe roast is warming up.\nTry again if it stays pending.",
    score: response.ai_score == null ? "..." : Number(response.ai_score).toFixed(1),
    aura: response.aura || "Pending Aura",
    tags: response.vibe_tags?.length ? response.vibe_tags : ["queued", "processing", response.status],
    tips: response.improvement_tips?.length
      ? response.improvement_tips
      : ["The backend accepted the post", "Celery will finish the roast shortly"],
    status: response.status,
  };
}
