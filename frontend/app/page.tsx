import { TranslatorForm } from "@/components/translator-form";

export default function HomePage() {
  return (
    <main className="container">
      <h1>PPT Translator BS MVP</h1>
      <p className="subtitle">Upload PPTX, run translation, and download translated PPTX.</p>
      <TranslatorForm />
    </main>
  );
}
