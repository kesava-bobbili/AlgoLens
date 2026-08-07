const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

function parseFastApiDetail(payload: unknown): string {
  if (!payload || typeof payload !== "object") {
    return "Request failed";
  }
  const detail = (payload as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        typeof item === "object" && item !== null && "msg" in item
          ? String((item as { msg: string }).msg)
          : JSON.stringify(item)
      )
      .join("; ");
  }
  return `Request failed (${JSON.stringify(detail)})`;
}

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  let res: Response;

  try {
    console.info("[AlgoLens API] Request", path);

    const isFormData =
      typeof FormData !== "undefined" && options?.body instanceof FormData;

    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: isFormData
        ? options?.headers
        : {
            "Content-Type": "application/json",
            ...options?.headers,
          },
    });
  } catch (e) {
    console.error("[AlgoLens API] network error", path, e);

    throw new Error(
      `Cannot reach API at ${API_BASE}. Is the backend running? (${
        e instanceof Error ? e.message : "network error"
      })`
    );
  }

  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));

    console.error("[AlgoLens API]", res.status, path, errBody);

    throw new Error(
      parseFastApiDetail(errBody) ?? `Request failed: ${res.status}`
    );
  }

  return res.json() as Promise<T>;
}

export interface AnalysisResult {
  pattern: string;
  confidence: string;
  time_complexity: string;
  space_complexity: string;
  ai_explanation: string;
  all_matches: Record<string, number>;
}

export interface TraceStep {
  step: number;
  line_number: number;
  line_content: string;
  variables: Record<string, string>;
  call_stack: string[];
  event: string;
}

export interface VisualizeResult {
  steps: TraceStep[];
  source_lines: string[];
  error: string | null;
  recursion_depth: number;
}

export interface InterviewStartResult {
  session_id: string;
  pattern: string;
  question: string;
}

export interface InterviewRespondResult {
  score: number | null;
  feedback: string;
  follow_up: string | null;
  done: boolean;
}

export interface GitHubMeta {
  full_name: string;
  description: string | null;
  language: string | null;
  stars: number;
  forks: number;
  topics: string[];
  default_branch: string;
  languages: Record<string, number>;
}

export interface GitHubAnalyzeResult {
  meta: GitHubMeta;
  file_tree: string[];
  ai_analysis: string;
}

export interface KnowledgeSource {
  source_id: string;
  filename: string;
  file_type: string;
  chunk_index: number;
  text: string;
  score: number;
}

export interface KnowledgeIngestResult {
  files_processed: number;
  chunks_indexed: number;
  skipped_files: string[];
  message: string;
}

export interface KnowledgeQueryResult {
  answer: string;
  sources: KnowledgeSource[];
  retrieval_count: number;
}

export interface SimilarProblemResult {
  matches: KnowledgeSource[];
}

export interface KnowledgeStatsResult {
  chunks: number;
  embedding_model: string;
  vector_store: string;
}

export const api = {
  analyze: (problem_text: string) =>
    request<AnalysisResult>("/api/v1/analyze", {
      method: "POST",
      body: JSON.stringify({ problem_text }),
    }),

  visualize: (code: string, stdin = "") =>
    request<VisualizeResult>("/api/v1/visualize/trace", {
      method: "POST",
      body: JSON.stringify({ code, stdin }),
    }),

  interviewStart: (problem_text: string) =>
    request<InterviewStartResult>("/api/v1/interview/start", {
      method: "POST",
      body: JSON.stringify({ problem_text }),
    }),

  interviewRespond: (session_id: string, answer: string) =>
    request<InterviewRespondResult>("/api/v1/interview/respond", {
      method: "POST",
      body: JSON.stringify({ session_id, answer }),
    }),

  githubAnalyze: async (repo_url: string) => {
    console.info("[AlgoLens API] POST github/analyze", {
      apiBase: API_BASE,
      repo_url,
    });
    try {
      return await request<GitHubAnalyzeResult>("/api/v1/github/analyze", {
        method: "POST",
        body: JSON.stringify({ repo_url }),
      });
    } catch (err) {
      console.error("[AlgoLens API] github/analyze failed", repo_url, err);
      throw err;
    }
  },

  knowledgeIngest: (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    return request<KnowledgeIngestResult>("/api/v1/knowledge/ingest", {
      method: "POST",
      body: formData,
    });
  },

  knowledgeQuery: (question: string, top_k = 5) =>
    request<KnowledgeQueryResult>("/api/v1/knowledge/query", {
      method: "POST",
      body: JSON.stringify({ question, top_k }),
    }),

  similarProblem: (problem_text: string, top_k = 5) =>
    request<SimilarProblemResult>("/api/v1/knowledge/similar", {
      method: "POST",
      body: JSON.stringify({ problem_text, top_k }),
    }),

  knowledgeStats: () =>
    request<KnowledgeStatsResult>("/api/v1/knowledge/stats"),

  patterns: () =>
    request<{ patterns: string[]; total: number }>("/api/v1/patterns"),
};
