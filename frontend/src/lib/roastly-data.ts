import type { LucideIcon } from "lucide-react";
import {
  Camera,
  FileText,
  Flame,
  Home,
  LampDesk,
  LayoutGrid,
  Shirt,
  Sparkles,
  UserRound,
} from "lucide-react";

export type RoastCategory =
  | "Roast My Outfit"
  | "Roast My Face"
  | "Roast My Setup"
  | "Roast My Resume"
  | "Roast My Dating Profile"
  | "Roast My Portfolio"
  | "Roast My Room"
  | "Roast My Bio";

export type RoastStyle =
  | "Friendly Roast"
  | "Brutal Roast"
  | "Gen Z Mode"
  | "Corporate Reviewer"
  | "Anime Villain"
  | "Therapist But Honest"
  | "British Insult Mode";

export type FeedPost = {
  id: number;
  author: string;
  handle: string;
  avatar: string;
  category: RoastCategory;
  style: RoastStyle;
  image: string;
  textPreview: string;
  roast: string;
  score: number;
  aura: string;
  tags: string[];
  tips: string[];
  reactions: number;
  comments: number;
  saves: number;
  heat: number;
  createdAt: string;
  featuredComment: {
    author: string;
    content: string;
    votes: number;
  };
};

export type CategoryConfig = {
  name: RoastCategory;
  shortName: string;
  icon: LucideIcon;
};

export const categories: CategoryConfig[] = [
  { name: "Roast My Outfit", shortName: "Outfit", icon: Shirt },
  { name: "Roast My Face", shortName: "Face", icon: Camera },
  { name: "Roast My Setup", shortName: "Setup", icon: LampDesk },
  { name: "Roast My Resume", shortName: "Resume", icon: FileText },
  { name: "Roast My Dating Profile", shortName: "Dating", icon: Sparkles },
  { name: "Roast My Portfolio", shortName: "Portfolio", icon: LayoutGrid },
  { name: "Roast My Room", shortName: "Room", icon: Home },
  { name: "Roast My Bio", shortName: "Bio", icon: UserRound },
];

export const roastStyles: RoastStyle[] = [
  "Friendly Roast",
  "Brutal Roast",
  "Gen Z Mode",
  "Corporate Reviewer",
  "Anime Villain",
  "Therapist But Honest",
  "British Insult Mode",
];

export const feedPosts: FeedPost[] = [
  {
    id: 1,
    author: "Mira",
    handle: "@mira.zip",
    avatar: "MZ",
    category: "Roast My Outfit",
    style: "Gen Z Mode",
    image:
      "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
    textPreview: "First day back on campus fit. Be honest.",
    roast:
      "The jacket is doing luxury, the pants are doing group project, and the shoes look like they have already emotionally graduated.",
    score: 7.8,
    aura: "Chaotic Campus Main Character",
    tags: ["thrift boss", "deadline energy", "espresso coded", "almost iconic"],
    tips: ["Swap one oversized piece for structure", "Let the shoes match the jacket's ambition"],
    reactions: 1840,
    comments: 316,
    saves: 94,
    heat: 98,
    createdAt: "8m",
    featuredComment: {
      author: "jay.exe",
      content: "The fit has tenure but the sneakers are still on academic probation.",
      votes: 422,
    },
  },
  {
    id: 2,
    author: "Drew",
    handle: "@drewbuilds",
    avatar: "DB",
    category: "Roast My Setup",
    style: "Corporate Reviewer",
    image:
      "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=80",
    textPreview: "Rate the battle station. Cable comments are banned.",
    roast:
      "This desk says senior engineer, but the cable routing says the onboarding doc is still a Google Doc named FINAL_v6_really.",
    score: 8.3,
    aura: "Productivity Theater With Receipts",
    tags: ["keyboard priest", "monitor maximalist", "standup survivor", "clean-ish"],
    tips: ["Add warmer lighting", "Hide the power brick before it files a complaint"],
    reactions: 1272,
    comments: 205,
    saves: 128,
    heat: 91,
    createdAt: "22m",
    featuredComment: {
      author: "nora",
      content: "The setup has OKRs and none of them mention cable ties.",
      votes: 311,
    },
  },
  {
    id: 3,
    author: "Kai",
    handle: "@kai.live",
    avatar: "KL",
    category: "Roast My Room",
    style: "Therapist But Honest",
    image:
      "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=80",
    textPreview: "Moved in two weeks ago. Does it have personality yet?",
    roast:
      "The room is calm, but in the way a notes app is calm before you add 47 life plans and one grocery list from 2023.",
    score: 8.0,
    aura: "Soft Launch Adulthood",
    tags: ["plant diplomacy", "ambient overthinker", "pinterest adjacent", "blank wall arc"],
    tips: ["Add one large art piece", "Use a stronger accent color so the room stops whispering"],
    reactions: 963,
    comments: 142,
    saves: 246,
    heat: 84,
    createdAt: "41m",
    featuredComment: {
      author: "sofia",
      content: "This room has healed from things it refuses to name.",
      votes: 190,
    },
  },
];

export const leaderboard = [
  { name: "jay.exe", stat: "24.8k XP", change: "+18%" },
  { name: "mira.zip", stat: "19.2k XP", change: "+12%" },
  { name: "nora", stat: "17.5k XP", change: "+9%" },
  { name: "drewbuilds", stat: "15.1k XP", change: "+7%" },
];

export const achievementCards = [
  { label: "Roast Streak", value: "6 days", icon: Flame, tone: "text-[#ffb020]" },
  { label: "Top Score", value: "9.1", icon: Sparkles, tone: "text-[#8fff7a]" },
  { label: "Viral Heat", value: "#12", icon: Flame, tone: "text-[#ff5b5a]" },
];

export const aiPreview = {
  roast:
    [
      "This profile has the confidence of a launch announcement.",
      "Sadly, it has the specificity of a weather app that refuses to load.",
      "The vibe is mysterious, but mostly because the personality forgot to clock in.",
      "It is trying to be charming and accidentally brought a clipboard.",
      "Give people one real detail before the algorithm files a missing-person report.",
    ].join("\n"),
  score: 6.8,
  aura: "Strategic Mystery Box",
  tags: ["soft flex", "almost charming", "bio under construction", "algorithm friendly"],
  tips: [
    "Add one concrete detail people can reply to",
    "Use a brighter first image or a sharper opening line",
  ],
};
