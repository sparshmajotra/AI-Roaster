import type { RoastCategory, RoastStyle } from "@/lib/roastly-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type CreateRoastPostPayload = {
  category: RoastCategory;
  roast_style: RoastStyle;
  visibility: "public" | "private" | "anonymous";
  text_content?: string;
  media?: File;
};

export type RoastPostResponse = {
  id: number;
  ai_roast: string;
  ai_score: string | number | null;
  aura: string;
  vibe_tags: string[];
  improvement_tips: string[];
  status: string;
};

export async function getDemoToken() {
  const response = await fetch(`${API_URL}/accounts/users/demo_token/`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`Demo login failed with status ${response.status}`);
  }

  return response.json() as Promise<{ access: string; refresh: string }>;
}

export async function createRoastPost(payload: CreateRoastPostPayload, token?: string) {
  const formData = new FormData();

  formData.set("category", payload.category);
  formData.set("roast_style", payload.roast_style);
  formData.set("visibility", payload.visibility === "anonymous" ? "public" : payload.visibility);
  formData.set("is_anonymous", String(payload.visibility === "anonymous"));

  if (payload.text_content) {
    formData.set("text_content", payload.text_content);
  }

  if (payload.media) {
    formData.set("media", payload.media);
  }

  const response = await fetch(`${API_URL}/roasts/posts/`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Roast request failed with status ${response.status}`);
  }

  return response.json() as Promise<RoastPostResponse>;
}

export async function fetchTrendingPosts() {
  const response = await fetch(`${API_URL}/roasts/posts/trending/`, {
    next: { revalidate: 30 },
  });

  if (!response.ok) {
    throw new Error(`Trending feed failed with status ${response.status}`);
  }

  return response.json();
}
