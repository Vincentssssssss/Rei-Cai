"use client";

import { FormEvent, useMemo, useState } from "react";

type StyleMode = "Balanced" | "Minimal" | "Full";

const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

function parseTerminology(input: string): Record<string, string> {
  const out: Record<string, string> = {};
  const lines = input
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  for (const line of lines) {
    const parts = line.split("=>");
    if (parts.length < 2) {
      continue;
    }
    const src = parts[0].trim();
    const tgt = parts.slice(1).join("=>").trim();
    if (src && tgt) {
      out[src] = tgt;
    }
  }
  return out;
}

export function TranslatorForm() {
  const [endpoint, setEndpoint] = useState("https://chataiapi.bcggc.com/api/llm-service/v1/chat/completions");
  const [model, setModel] = useState("deepseek-v4-flash");
  const [apiKey, setApiKey] = useState("");
  const [sourceLanguage, setSourceLanguage] = useState("Chinese (Simplified)");
  const [targetLanguage, setTargetLanguage] = useState("English");
  const [batchSize, setBatchSize] = useState(12);
  const [maxWorkers, setMaxWorkers] = useState(3);
  const [retry, setRetry] = useState(3);
  const [translationStyle, setTranslationStyle] = useState<StyleMode>("Balanced");
  const [terminologyText, setTerminologyText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const endpointUrl = useMemo(() => `${backendBaseUrl}/api/v1/translate/pptx`, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    if (!file) {
      setError("Please choose a .pptx file.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".pptx")) {
      setError("Only .pptx files are supported.");
      return;
    }

    setIsSubmitting(true);
    try {
      const options = {
        endpoint,
        model,
        api_key: apiKey,
        source_language: sourceLanguage,
        target_language: targetLanguage,
        batch_size: batchSize,
        max_workers: maxWorkers,
        retry,
        translation_style: translationStyle,
        terminology: parseTerminology(terminologyText),
        force_terminology_replace: true
      };

      const formData = new FormData();
      formData.append("file", file);
      formData.append("options_json", JSON.stringify(options));

      const response = await fetch(endpointUrl, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Request failed (${response.status}): ${text}`);
      }

      const blob = await response.blob();
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = file.name.replace(/\.pptx$/i, "_translated.pptx");
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(downloadUrl);
      setSuccess("Translation completed. Download started.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unknown error.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="form" onSubmit={onSubmit}>
      <section className="grid">
        <label>
          Endpoint
          <input value={endpoint} onChange={(e) => setEndpoint(e.target.value)} required />
        </label>
        <label>
          Model
          <input value={model} onChange={(e) => setModel(e.target.value)} required />
        </label>
        <label>
          API Key
          <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
        </label>
        <label>
          Source language
          <input value={sourceLanguage} onChange={(e) => setSourceLanguage(e.target.value)} required />
        </label>
        <label>
          Target language
          <input value={targetLanguage} onChange={(e) => setTargetLanguage(e.target.value)} required />
        </label>
        <label>
          Batch size
          <input
            type="number"
            min={1}
            max={100}
            value={batchSize}
            onChange={(e) => setBatchSize(Number(e.target.value))}
            required
          />
        </label>
        <label>
          Max workers
          <input
            type="number"
            min={1}
            max={16}
            value={maxWorkers}
            onChange={(e) => setMaxWorkers(Number(e.target.value))}
            required
          />
        </label>
        <label>
          Retry
          <input
            type="number"
            min={1}
            max={10}
            value={retry}
            onChange={(e) => setRetry(Number(e.target.value))}
            required
          />
        </label>
        <label>
          Translation style
          <select value={translationStyle} onChange={(e) => setTranslationStyle(e.target.value as StyleMode)}>
            <option value="Balanced">Balanced</option>
            <option value="Minimal">Minimal</option>
            <option value="Full">Full</option>
          </select>
        </label>
      </section>

      <label>
        Terminology (one per line: source =&gt; target)
        <textarea
          rows={5}
          value={terminologyText}
          onChange={(e) => setTerminologyText(e.target.value)}
          placeholder={"净利润 => net profit\n营业收入 => revenue"}
        />
      </label>

      <label>
        PPTX file
        <input type="file" accept=".pptx" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required />
      </label>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Translating..." : "Translate and Download"}
      </button>

      <p className="hint">Backend: {backendBaseUrl}</p>
      {error ? <p className="error">{error}</p> : null}
      {success ? <p className="success">{success}</p> : null}
    </form>
  );
}
